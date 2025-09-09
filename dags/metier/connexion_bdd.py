from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result, Transaction
import pandas as pd
from typing import List
import os

class ConnexionBDD:

    def __init__(self):
        # Connexion au serveur
        host=os.getenv("PG_METIER_SERVER")
        dbname=os.getenv("PG_METIER_BASE")
        user=os.getenv("PG_METIER_USER")
        password=os.getenv("PG_METIER_PASSWORD")
        self._moteur = create_engine(f"postgresql://{user}:{password}@{host}/{dbname}")
        self._connexion = self._moteur.connect()                

    def begin_transaction(self) -> Transaction:
        return self._connexion.begin()

    def commit(self, transaction: Transaction) -> None:
        transaction.commit()

    def rollback(self, transaction: Transaction) -> None:
        transaction.rollback()

    def _liste_champs_depuis_donnees(self, donnees: dict | List[dict])-> list:
        if donnees is dict:
            premier_enregistrement = donnees
        else:
            premier_enregistrement = donnees[0]
        return premier_enregistrement.keys()

    def insert(self, nom_table: str, donnees: dict | List[dict])-> None:

        liste_champs = self._liste_champs_depuis_donnees(donnees)

        def traiter_enregistrement(enregistrement: dict)-> None:
            # chaine_sql = (
            #     f"insert into {nom_table} ({",".join(liste_champs)})"
            #     + f" values ({", ".join([":"+nom_champ for nom_champ in liste_champs])})"
            # )
            
            #chaine_sql = f"insert into {nom_table} ({",".join(liste_champs)}) values ({", ".join([":"+nom_champ for nom_champ in liste_champs])})"
            
            chaine_sql = "insert into "+nom_table+" ("+",".join(liste_champs)+") values ("+", ".join([":"+nom_champ for nom_champ in liste_champs])+")"            
            
            print(chaine_sql)
            self.executer_requete(chaine_sql, enregistrement)

        if donnees is dict:
            traiter_enregistrement(donnees)
        else:
            for enreg in donnees:
                traiter_enregistrement(enreg)

    def executer_requete(self, chaine_sql: str, parametres: dict = None)-> Result:
        if parametres:
            return self._connexion.execute(text(chaine_sql), **parametres)
        else:
            return self._connexion.execute(text(chaine_sql))
    
    def resultat_dans_dataframe(resultat_requete: Result)-> pd.DataFrame:
        return pd.DataFrame(resultat_requete.fetchall(), columns=resultat_requete.keys())

    # def _nouveau_curseur(self) -> cursor:
    #     return self._moteur.cursor(cursor_factory=DictCursor)
    
    def charger_structure_table(self, nom_table)-> pd.DataFrame:
        return pd.read_sql(f"select * from {nom_table} limit 0", con=self._moteur)