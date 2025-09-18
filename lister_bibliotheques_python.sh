#!/bin/sh

docker compose -f compose_dev.yaml --env-file .env.dev exec airflow_scheduler_dev bash -c "pip freeze"