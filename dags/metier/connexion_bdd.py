from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result, Transaction
import pandas as pd
from typing import List, Callable
import os
import random

class ConnexionBDD:

    def __init__(self):
        # Connexion au serveur
        host=os.getenv("PG_METIER_SERVER")
        self._nom_base=os.getenv("PG_METIER_BASE")
        user=os.getenv("PG_METIER_USER")
        password=os.getenv("PG_METIER_PASSWORD")
        self._moteur = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{self._nom_base}")
        self._connexion = self._moteur.connect()                

    def begin_transaction(self) -> Transaction:
        return self._connexion.begin()

    def commit(self, transaction: Transaction) -> None:
        transaction.commit()

    def rollback(self, transaction: Transaction) -> None:
        transaction.rollback()

    def fermer(self) -> None:
        self._connexion.close()

    def _liste_champs_depuis_donnees(self, donnees: dict | List[dict])-> list:
        if isinstance(donnees, dict):
            premier_enregistrement = donnees
        else:
            premier_enregistrement = donnees[0]
        return premier_enregistrement.keys()
    
    def select_table(self, nom_table: str, limite: int = 0)-> Result:
        chaine_sql = "select * from "+nom_table
        if limite:
            chaine_sql += ' limit :limite'
        return self.executer_requete(chaine_sql, {"limite": limite})

    def insert(self, nom_table: str, donnees: dict | List[dict])-> None:

        liste_champs = self._liste_champs_depuis_donnees(donnees)

        def traiter_enregistrement(enregistrement: dict)-> None:            
            chaine_sql = "insert into "+nom_table+" ("+",".join(liste_champs)+") values ("+", ".join([":"+nom_champ for nom_champ in liste_champs])+")"            
            self.executer_requete(chaine_sql, enregistrement)

        if isinstance(donnees, dict):
            traiter_enregistrement(donnees)
        else:
            for enreg in donnees:
                traiter_enregistrement(enreg)

    def update(self, nom_table: str, donnees: dict | List[dict], liste_champs_table: List[dict] = None)-> None:
        if liste_champs_table is None:
            liste_champs_table = self.champs_table(nom_table)

        def traiter_enregistrement(enregistrement: dict)-> None:
            chaine_sql = "update "+nom_table+" set "
            chaine_separateur = ""
            for nom_champ in enregistrement:
                if not self.champ_est_pk(nom_champ, liste_champs_table):
                    chaine_sql += f"{chaine_separateur}{nom_champ} = :{nom_champ}"      
                    chaine_separateur = ", "
            chaine_sql += " where"
            chaine_separateur = ""
            for nom_champ, valeur_champ in enregistrement.items():
                if self.champ_est_pk(nom_champ, liste_champs_table):
                    chaine_sql += f" {chaine_separateur}{nom_champ} = :{nom_champ}"      
                    chaine_separateur = "and "
            self.executer_requete(chaine_sql, enregistrement)

        if isinstance(donnees, dict):
            traiter_enregistrement(donnees)
        else:
            for enreg in donnees:
                traiter_enregistrement(enreg)

    def upsert(self, nom_table: str, donnees: dict | List[dict], liste_champs_table: List[dict] = None)-> None:

        #liste_champs = self._liste_champs_depuis_donnees(donnees)
        if liste_champs_table is None:
            liste_champs_table = self.champs_table(nom_table)

        def traiter_enregistrement(enregistrement: dict)-> None:
            if self.enregistrement_existe(nom_table, self.valeurs_pk(enregistrement, liste_champs_table)):
                self.update(nom_table, enregistrement, liste_champs_table=liste_champs_table)
            else:
                self.insert(nom_table, enregistrement)

        if isinstance(donnees, dict):
            traiter_enregistrement(donnees)
        else:
            for enreg in donnees:
                traiter_enregistrement(enreg)

    def executer_requete(self, chaine_sql: str, parametres: dict = None)-> Result:
        if parametres:
            return self._connexion.execute(text(chaine_sql), **parametres)
        else:
            return self._connexion.execute(text(chaine_sql))
        
    def champs_table(self, nom_table: str)-> List[dict]:
        chaine_sql = """
            select distinct
                colonne.column_name,
                colonne.data_type,
                coalesce(
                    (
                        select true
                        from
                            information_schema.key_column_usage colonne_u
                            inner join information_schema.table_constraints table_c
                                on table_c.table_catalog = colonne_u.table_catalog 
                                and table_c.table_schema = colonne_u.table_schema 
                                and table_c.table_name = colonne_u.table_name
                                and table_c.constraint_name = colonne_u.constraint_name
                        where
                            colonne_u.table_catalog = colonne.table_catalog 
                            and colonne_u.table_schema = colonne.table_schema 
                            and colonne_u.table_name = colonne.table_name
                            and colonne_u.column_name = colonne.column_name
                            and table_c.constraint_type = 'PRIMARY KEY'
                    ),
                    false
                ) is_pk,
                coalesce(
                    (
                        select true
                        from
                            information_schema.key_column_usage colonne_u
                            inner join information_schema.table_constraints table_c
                                on table_c.table_catalog = colonne_u.table_catalog 
                                and table_c.table_schema = colonne_u.table_schema 
                                and table_c.table_name = colonne_u.table_name
                                and table_c.constraint_name = colonne_u.constraint_name
                        where
                            colonne_u.table_catalog = colonne.table_catalog 
                            and colonne_u.table_schema = colonne.table_schema 
                            and colonne_u.table_name = colonne.table_name
                            and colonne_u.column_name = colonne.column_name
                            and table_c.constraint_type = 'UNIQUE'
                    ),
                    false
                ) is_unique
            from
                information_schema.columns colonne
            where
                colonne.table_catalog = :nom_base
                and colonne.table_schema = 'public'
                and colonne.table_name = :nom_table
        """
        return self.executer_requete(chaine_sql, {'nom_base': self._nom_base, 'nom_table': nom_table}).mappings().fetchall()
    
    def liste_champs_pk(self, liste_champs_table: List[dict])-> List[dict]:
        return [champ for champ in liste_champs_table if champ["is_pk"]]
    
    def liste_noms_champs_pk(self, liste_champs_table: List[dict])-> str:
        return [champ["column_name"] for champ in self.liste_champs_pk(liste_champs_table)]

    def champ_est_pk(self, nom_champ: str, liste_champs_table: List[dict])-> bool:
        return nom_champ in self.liste_noms_champs_pk(liste_champs_table)
    
    def valeurs_pk(self, enregistrement: dict, liste_champs_table: List[dict])-> dict:
        resultat = {}
        for nom, valeur in enregistrement.items():
            if self.champ_est_pk(nom, liste_champs_table):
                resultat[nom] = valeur
        return resultat

    def appliquer_types_champs_dans_df(self, df: pd.DataFrame, nom_table: str, format_date_time: str = None, supprimer_colonnes_inconnues: bool = False, fct_on_colonne_supprimee: Callable = None)-> None:
        liste_champs: List[dict] = self.champs_table(nom_table)
        if supprimer_colonnes_inconnues:
            for nom_colonne in df.columns:
                if nom_colonne not in [champ["column_name"] for champ in liste_champs]:
                    df.drop(columns=[nom_colonne], inplace=True)
                    if fct_on_colonne_supprimee:
                        fct_on_colonne_supprimee(nom_colonne)
        for champ in liste_champs:
            if champ["column_name"] in df.columns:
                if champ["data_type"] == "boolean":
                    df[champ["column_name"]] = df[champ["column_name"]].replace({0: False, 1: True})
                elif champ["data_type"] == "character varying":
                    df[champ["column_name"]] = df[champ["column_name"]].astype(str)
                elif champ["data_type"] == "date":
                    if format_date_time is None:
                        raise Exception('Format de date/heure non fourni.')
                    df[champ["column_name"]] = pd.to_datetime(df[champ["column_name"]], format=format_date_time, errors='coerce')
    def table_existe(self, nom_table: str)-> bool:
        chaine_sql = "select 1 from information_schema.tables where table_name = :nom_table"
        return len(self.executer_requete(chaine_sql, {"nom_table": nom_table}).all())
    
    def enregistrement_existe(self, nom_table: str, valeurs_cles_primaires: dict)-> bool:
        liste_champs = valeurs_cles_primaires.keys()
        chaine_sql = f"select true from {nom_table} where 1=1"
        for nom_champ in liste_champs:
            chaine_sql += f" and {nom_champ} = :{nom_champ}"
        parametres = valeurs_cles_primaires
        parametres["nom_table"] = nom_table
        return len(self.executer_requete(chaine_sql, parametres).all())

    def enregistrer_df_dans_table(self, df: pd.DataFrame, nom_table: str, verifier_existance_enregistrement: bool)-> None:
        
        def upsert_pg(liste_champs_table: List[dict]):
            # on définie une table tempo pour pandas en la créant avec la structure de la table d'origine
            table_tempo_valide = False
            while not table_tempo_valide:
                nom_table_temporaire = f"temp_{nom_table}_{random.randint(0, 1000)}"
                table_tempo_valide = not self.table_existe(nom_table_temporaire)
            self.executer_requete(
                f"select {nom_table}.* into {nom_table_temporaire} from {nom_table} limit 0"
            )
            # décharge le df dans la table tempo
            df.to_sql(nom_table_temporaire, con=self._connexion, if_exists="append", index=False, chunksize=1000, method="multi")
            chaine_sql = f"""
                insert into {nom_table} ({', '.join(df.columns)})
                select {', '.join(df.columns)} FROM {nom_table_temporaire}
                on conflict ({', '.join(self.liste_noms_champs_pk(liste_champs_table))}) do update
                set
            """
            chaine_sql += ' ,'.join([f"{colonne} = excluded.{colonne}" for colonne in df.columns])
            self.executer_requete(chaine_sql)
            self.executer_requete(f"drop table {nom_table_temporaire}")

        if verifier_existance_enregistrement:
            liste_champs_table = self.champs_table(nom_table)
            if True: # on peut sous-traiter à pg
                upsert_pg(liste_champs_table)
            else:
                for _, enregistrement in df.iterrows():
                    self.upsert(nom_table, enregistrement.to_dict(), liste_champs_table=liste_champs_table)
        else:
            df.to_sql(nom_table, con=self._connexion, if_exists="append", index=False, chunksize=1000, method="multi")