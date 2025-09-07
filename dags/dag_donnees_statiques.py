from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from metier.donnees_statiques import test1, test2, test3

default_args = {
    "owner": "airflow",
    "retries": 1,
    #'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="donnees_statiques",
    default_args=default_args,
    description="DAG appelant test1 toutes les minutes",
    schedule_interval=timedelta(minutes=1),
    start_date=datetime(2024, 6, 1),
    catchup=False,
    tags=["example"],
) as dag:
    run_test1 = PythonOperator(
        task_id="run_test1",
        python_callable=test1
    )

    run_test1
