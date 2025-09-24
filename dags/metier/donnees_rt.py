from __future__ import annotations
from typing import List
import os
import pandas
from datetime import datetime
import requests
from google.transit import gtfs_realtime_pb2
from metier import utils
from metier.utils_bdd import ConnexionBDDMetier


# def exemple()-> None:
#     connexion = ConnexionBDDMetier()
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

def traiter_donnees_rt(**kwargs)-> None:

    def gestion_url(connexion: ConnexionBDDMetier, compagnie: dict)-> None:

        def verification_enregistrement(enregistrement)-> bool:
            chaine_sql = """
                select 1
                from
                    stop_times
                    inner join trips
                        on trips.id_compagnie = stop_times.id_compagnie
                        and trips.trip_id = stop_times.trip_id
                where
                    stop_times.id_compagnie = :id_compagnie
                    and stop_times.trip_id = :trip_id
                    and stop_times.stop_id = :stop_id
                    and trips.route_id = :route_id
            """
            parametres = {
                "id_compagnie": compagnie["id_compagnie"],
                "trip_id": enregistrement["trip_id"],
                "stop_id": enregistrement["stop_id"],
                "route_id": enregistrement["route_id"]
            }
            return len(connexion.executer_requete(chaine_sql, parametres).all()) > 0

        utils.log_infos_compagnie(compagnie, f"Traitement URL RT : {compagnie['url_rt']}")
        reponse = requests.get(compagnie['url_rt'])
        feed_trips = gtfs_realtime_pb2.FeedMessage()
        feed_trips.ParseFromString(reponse.content)

        enregs = []
        for entity in feed_trips.entity:
            #enregs.append({entity})
            if entity.HasField("trip_update"):
                trip_id = entity.trip_update.trip.trip_id
                route_id = entity.trip_update.trip.route_id

                for stu in entity.trip_update.stop_time_update:
                    stop_id = stu.stop_id

                    if stu.HasField("arrival") and stu.arrival.HasField("time"):
                        realtime_arrival = datetime.fromtimestamp(stu.arrival.time)
                        #realtime_arrival = realtime_arrival.astimezone(gtfs_tz)
                        enregs.append(
                            {
                                "id_compagnie": compagnie["id_compagnie"],
                                "trip_id": trip_id,
                                "route_id": route_id,
                                "stop_id": stop_id,
                                "arrival": realtime_arrival,
                                # "record_time": now_local,
                            }
                        )
        nb_enregs = len(enregs)
        if nb_enregs == 0:
            utils.log_infos_compagnie(compagnie, "Pas de données à traiter.")
        else:
            utils.log_infos_compagnie(compagnie, f"Nb enregistrements à traiter : {nb_enregs}")
            df = pandas.DataFrame(enregs)
            #print(df.head(20))
            connexion.appliquer_types_champs_dans_df(df, 'rt_trip_update')

            # on peut avoir plusieurs date-heures d'arrivée pour un même trip_id/route_id/stop_id, ce qui n'est pas normal
            # On garde une seule date-heure (la date-heure la plus grande)
            df = df.sort_values(by='arrival', ascending=False)
            df = df.drop_duplicates(subset=['id_compagnie', 'trip_id', 'route_id', 'stop_id'])

            df['calc_valide'] = df.apply(verification_enregistrement, axis=1)
            for _, enregistrement in df.iterrows():
                if not enregistrement["calc_valide"]:
                    utils.log_warning_compagnie(compagnie, "Données invalides non prises en compte :")
                    utils.log_warning_compagnie(compagnie, f"trip_id={enregistrement['trip_id']} route_id={enregistrement['route_id']} stop_id={enregistrement['stop_id']}")
            df = df[df["calc_valide"] == True]
            df = df.drop(columns=['calc_valide'])
            connexion.enregistrer_df_dans_table(df, 'rt_trip_update', True)
            utils.log_infos_compagnie(compagnie, f"Nb enregistrements enregistrés : {len(df)}")


    # logical_date = kwargs.get('logical_date') kwargs récupère les infos de contexte d'airflow
    connexion = ConnexionBDDMetier()
    exception = None
    transaction = None
    for compagnie in connexion.compagnies:
        try:
            utils.log_infos_compagnie(compagnie, "DEBUT import des données dynamiques")
            transaction = connexion.begin_transaction()
            gestion_url(connexion, compagnie)
            connexion.commit(transaction)
            utils.log_infos_compagnie(compagnie, "FIN import des données dynamiques")
        except Exception as e:
            if transaction:
                connexion.rollback(transaction)
            utils.log_warning_compagnie(compagnie, "Une erreur est survenue, traitement annulé pour cette compagnie.")
            exception = e
            break
    connexion.fermer()
    if exception is not None:
        raise exception