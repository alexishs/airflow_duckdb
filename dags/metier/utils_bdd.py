from __future__ import annotations
from typing import List
import os
from metier.utils import chemin_dags
from metier.connexion_bdd import ConnexionBDD

class ConnexionBDDMetier(ConnexionBDD):
    def __init__(self):
        super().__init__()
        self._compagnies: List[dict] = []

    def gestion_configuration(self)-> None:
        transaction = self.begin_transaction()
        try:
            chaine_sql = (
                """
                SELECT count(*) nb_tables
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                """
            )
            nb_tables = self.executer_requete(chaine_sql).first()["nb_tables"]
            if nb_tables == 0:
                with open(chemin_dags("initialisation_base.sql"), "r", encoding="utf-8") as script:
                    self.executer_requete(script.read())
                # On va rechercher les entités par défaut
                liste_libelles = os.getenv('GTFS_LIBELLES').split(";")
                liste_urls_statiques = os.getenv('GTFS_URLS_INFOS_STATIQUES').split(";")
                liste_urls_rt = os.getenv('GTFS_URLS_RT').split(";")
                nb_entites = len(liste_libelles)
                if not(nb_entites == len(liste_urls_statiques) == len(liste_urls_rt)):
                    raise Exception("Infos compagnies par défaut non concordantes.")
                enregs_entite = []
                for index_entite in range(nb_entites):
                    enregs_entite.append({
                        "id_compagnie" : index_entite + 1,
                        "libelle_compagnie" : liste_libelles[index_entite],
                        "url_donnees_statiques" : liste_urls_statiques[index_entite],
                        "url_rt" : liste_urls_rt[index_entite]
                    })
                self.insert('compagnie', enregs_entite)
                self.commit(transaction)
        except Exception as e:
            self.rollback(transaction)
            raise e # on renvoie l'exception

    @property
    def compagnies(self)-> List[dict]:
        if not self._compagnies:
            self._compagnies = self.select_table('compagnie').mappings().fetchall()
        return self._compagnies

def configurer_bdd()->None:
    connexion = ConnexionBDDMetier()
    exception = None
    try:
        connexion.gestion_configuration()
    except Exception as e:
        exception = e
    connexion.fermer()
    if exception is not None:
        raise exception