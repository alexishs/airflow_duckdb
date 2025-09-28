from __future__ import annotations
from typing import List
import os
import pandas
from pathlib import Path
from datetime import datetime
import requests
import zipfile
from metier import utils
from metier.utils_bdd import ConnexionBDDMetier

NOM_FICHIER_ZIP_DONNEES_STATIQUES = "donnees_statiques.zip"
LISTE_TABLES_DONNEES_STATIQUES = ("agency", "calendar", "calendar_dates", "feed_info", "routes", "shapes", "stops", "trips", "stop_times")


# def exemple()-> None:
#     connexion = ConnexionBDD()
#     transaction = connexion.begin_transaction()
#     exception = None
#     try:
#         pass
#         connexion.commit(transaction)
#     except Exception as e:
#         connexion.rollback(transaction)
#         exception = e
#     connexion.fermer()
#     if exception is not None:
#         raise exception


def telecharger_donnees_statiques()-> None:
    connexion = ConnexionBDDMetier()
    #transaction = connexion.begin_transaction() pas nécessaire ici
    exception = None
    try:
        # on vérifie qu'il n'y a pas de vieux fichiers avant de commencer
        for compagnie in connexion.compagnies:
            repertoire = utils.chemin_cache_compagnie(compagnie, "")
            if Path(repertoire).exists():
                raise Exception(f"Ancien répertoire {repertoire} encore éxistant.")
        # on commence
        for compagnie in connexion.compagnies:
            chemin_fichier_zip = utils.chemin_cache_compagnie(compagnie, NOM_FICHIER_ZIP_DONNEES_STATIQUES)
            reponse = requests.get(compagnie["url_donnees_statiques"])
            if reponse.status_code != 200:
                utils.log_warning_compagnie(compagnie, f"Erreur récupération fichier (erreur HTTP {reponse.status_code})")
            else:
                Path(utils.chemin_cache_compagnie(compagnie, "")).mkdir(parents=True)
                with open(chemin_fichier_zip, "wb") as fichier:
                    fichier.write(reponse.content)
                with zipfile.ZipFile(chemin_fichier_zip, 'r') as fichier:
                    fichier.extractall(utils.chemin_cache_compagnie(compagnie, ""))
                os.remove(chemin_fichier_zip)
                utils.log_infos_compagnie(compagnie, f"Fichier {chemin_fichier_zip} décompressé et supprimmé.")
        #connexion.commit(transaction)
    except Exception as e:
        #connexion.rollback(transaction)
        exception = e
    connexion.fermer()
    if exception is not None:
        raise exception
    
def enregistrer_donnees_statiques_en_bdd()-> None:

    def chemin_fichier_table(compagnie: dict, nom_table: str)-> str:
        return utils.chemin_cache_compagnie(compagnie, f"{nom_table}.txt")
    
    def vider_table(nom_table: str, compagnie: dict)-> None:
        connexion.executer_requete(
            f"delete from {nom_table} where id_compagnie = :id_compagnie",
            {"id_compagnie": compagnie["id_compagnie"]}
        )

    def gestion_table(nom_table: str, connexion: ConnexionBDDMetier, compagnie: dict)-> bool:

        def champ_chaine_time_vers_interval(valeur)-> str:
            # chaine de type xx:xx:xx
            heures = int(valeur[0:2])
            minutes = int(valeur[3:5])
            secondes = int(valeur[6:8])
            jour = 0
            if (heures > 23):
                jour = 1
                heures -= 24
            en_secondes = (jour * 24 * 60 * 60) + (heures * 60 * 60) + (minutes * 60) + secondes
            return f"{en_secondes} seconds"

        chemin_fichier_csv = chemin_fichier_table(compagnie, nom_table)
        if Path(chemin_fichier_csv).exists():
            utils.log_infos_compagnie(compagnie, f"DEBUT traitement table {nom_table}…")
            df = pandas.read_csv(chemin_fichier_csv)

            df['id_compagnie'] = compagnie['id_compagnie']

            # renommage des colonnes
            if nom_table == "calendar_dates":
                df = df.rename(columns={'date': 'date_service'})
            # Cas particuliers
            if nom_table == "stop_times":
                # champ time en datetime (pour les heures du jour 0 après 23:59, on passe au jour 1)
                df['departure_time'] = df['departure_time'].apply(champ_chaine_time_vers_interval)
                df['arrival_time'] = df['arrival_time'].apply(champ_chaine_time_vers_interval)

            connexion.appliquer_types_champs_dans_df(
                df,
                nom_table,
                format_date_time='%Y%m%d',
                supprimer_colonnes_inconnues=True,
                fct_on_colonne_supprimee=
                    lambda nom_colonne:
                        utils.log_warning_compagnie(compagnie, f"La colonne '{nom_colonne}' du fichier {chemin_fichier_csv} est absente de la table est ne sera pas importée !")
            )
            # Particularités après formatage
            if nom_table == "stops":
                df['stop_timezone'] = df['stop_timezone'].replace('nan', None)
            connexion.enregistrer_df_dans_table(df, nom_table, verifier_existance_enregistrement=True) # on a supprimé les enregistrements avant.
            utils.log_infos_compagnie(compagnie, f"FIN traitement table {nom_table}.")
            return True
        else:
            return False

    connexion = ConnexionBDDMetier()
    exception = None
    transaction = None
    for compagnie in connexion.compagnies:
        liste_tables_traitees = []
        try:
            if not Path(utils.chemin_cache_compagnie(compagnie, "")).exists():
                utils.log_warning_compagnie(compagnie, "Le répertoire de cache n'éxiste pas.")
            else:
                # utils.log_infos_compagnie(compagnie, "DEBUT suppression des anciennes données statiques…")
                # for nom_table in reversed(LISTE_TABLES_DONNEES_STATIQUES):
                #     vider_table(nom_table, compagnie)
                # utils.log_infos_compagnie(compagnie, "FIN suppression des anciennes données statiques.")
                utils.log_infos_compagnie(compagnie, "DEBUT import des données statiques…")
                transaction = connexion.begin_transaction()
                for nom_table in LISTE_TABLES_DONNEES_STATIQUES:
                    if gestion_table(nom_table, connexion, compagnie):
                        liste_tables_traitees.append(nom_table)
                connexion.commit(transaction)
                utils.log_infos_compagnie(compagnie, "FIN import des données statiques")
                # on supprime en dernier la liste des fichiers traités
                for nom_table in liste_tables_traitees:
                    os.remove(chemin_fichier_table(compagnie, nom_table))
                utils.log_infos_compagnie(compagnie, "Les fichiers statiques sont supprimés.")
                if len(os.listdir(utils.chemin_cache_compagnie(compagnie, ""))):
                    utils.log_warning_compagnie(compagnie, "Le répertoire de cache contient des fichiers supplémentaires non traités !")
                else:
                    os.rmdir(utils.chemin_cache_compagnie(compagnie, ""))
        except Exception as e:
            if transaction:
                connexion.rollback(transaction)
            utils.log_warning_compagnie(compagnie, "Une erreur est survenue, traitement annulé pour cette compagnie.")
            exception = e
            break
    connexion.fermer()
    if exception is not None:
        raise exception