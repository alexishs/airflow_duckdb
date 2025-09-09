from __future__ import annotations
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from metier.config_bdd import configurer_bdd

default_args = {
    "owner": "airflow",
    "retries": 1,
    #'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="donnees_statiques",
    default_args=default_args,
    description="Gestion des données statiques",
    schedule_interval=timedelta(minutes=1),
    start_date=datetime(2024, 6, 1),
    catchup=False,
) as dag:
    run_config_bdd = PythonOperator(
        task_id="run_config_bdd",
        python_callable=configurer_bdd
    )
    run_config_bdd