#!/bin/sh

./supprimer_conteneurs_dev.sh 
docker image prune -a
docker volume prune -a
./creer_demarrer_conteneurs_dev.sh