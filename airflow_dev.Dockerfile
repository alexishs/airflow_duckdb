FROM apache/airflow:2.10.2-python3.9

ARG AIRFLOW_UID=50000

USER root
RUN usermod -u "$AIRFLOW_UID" -g 0 airflow && chown "$AIRFLOW_UID":0 -R /home/airflow && chown "$AIRFLOW_UID":0 -R /opt/airflow
# RUN usermod -u 1001 -g 0 airflow && chown 1001:0 -R /home/airflow && chown 1001:0 -R /opt/airflow

USER airflow
# pas nécessaire RUN bash -c "mkdir /opt/airflow/dags && mkdir /opt/airflow/logs && mkdir /opt/airflow/duckdb && mkdir /opt/airflow/warehouse && mkdir /opt/airflow/exports"
# pas nécessaire l'utilisateur airflow éxiste déjà ds l'image d'origine ENV PATH="/home/app_user/.local/bin:${PATH}"

RUN pip install psycopg2-binary pandas pyarrow requests gtfs-realtime-bindings