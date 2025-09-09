import os
from metier.utils import en_test
from metier.connexion_bdd import ConnexionBDD

def configurer_bdd()-> None:
    connexion = ConnexionBDD()
    transaction = connexion.begin_transaction()
    try:
        chaine_sql = (
            """
            SELECT count(*) nb_tables
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            """
        )
        nb_tables = connexion.executer_requete(chaine_sql).first()["nb_tables"]
        if nb_tables == 0:
            if en_test():
                chemin_script = "initialisation_base.sql"
            else:
                chemin_script = "/opt/airflow/dags/initialisation_base.sql"
            with open(chemin_script, "r", encoding="utf-8") as script:
                connexion.executer_requete(script.read())
            # On va rechercher les entités par défaut
            liste_libelles = os.getenv('GTFS_LIBELLES').split(";")
            liste_urls_statiques = os.getenv('GTFS_URLS_INFOS_STATIQUES').split(";")
            liste_urls_rt = os.getenv('GTFS_URLS_RT').split(";")
            nb_entites = len(liste_libelles)
            if not(nb_entites == len(liste_urls_statiques) == len(liste_urls_rt)):
                raise Exception("Infos entités par défaut non concordantes.")
            enregs_entite = []
            for index_entite in range(nb_entites):
                enregs_entite.append({
                    "id_entite" : index_entite,
                    "libelle_entite" : liste_libelles[index_entite],
                    "url_donnees_statiques" : liste_urls_statiques[index_entite],
                    "url_rt" : liste_urls_rt[index_entite]
                })
            connexion.insert('entite', enregs_entite)
            connexion.commit(transaction)
    except Exception as e:
        connexion.rollback(transaction)
        raise e # on renvoie l'exception
    finally:
        connexion = None