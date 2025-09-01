# airflow_duckdb

python3 ./generer_cles_secretes.py

docker compose -f docker-compose.yaml --env-file .env.dev build
docker compose -f docker-compose.yaml --env-file .env.dev up -d
docker compose -f docker-compose.yaml --env-file .env.dev run airflow-webserver airflow db init
docker compose -f docker-compose.yaml --env-file .env.dev run airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin


docker compose -f docker-compose.yaml --env-file .env.dev up -d