#!/bin/sh

docker compose -f compose_dev.yaml --env-file .env.dev up --build -d