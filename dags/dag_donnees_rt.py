from __future__ import annotations
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from metier.utils_bdd import configurer_bdd
from metier.donnees_rt import traiter_donnees_rt

default_args = {
    "owner": "airflow",
    "retries": 1,
    #'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="donnees_rt",
    default_args=default_args,
    description="Gestion des données temps réel",
    schedule_interval=timedelta(minutes=15),
    #schedule=None, mode manuel
    start_date=datetime(2024, 6, 1),
    catchup=False
) as dag:
    run_traiter_donnees_rt = PythonOperator(
        task_id="run_traiter_donnees_rt",
        python_callable=traiter_donnees_rt,
    )
    # run_telecharger_donnees_statiques = PythonOperator(
    #     task_id="run_telecharger_donnees_statiques",
    #     python_callable=telecharger_donnees_statiques
    # )
    # run_enregistrer_donnees_statiques_en_bdd = PythonOperator(
    #     task_id="run_enregistrer_donnees_statiques_en_bdd",
    #     python_callable=enregistrer_donnees_statiques_en_bdd
    # )

    run_traiter_donnees_rt #>> run_telecharger_donnees_statiques >> run_enregistrer_donnees_statiques_en_bdd