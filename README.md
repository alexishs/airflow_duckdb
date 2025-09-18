# airflow_duckdb

python3 ./generer_cles_secretes.py


Pour développer en local les DAGs :

La racine du projet python se situe dans le sous-dossier dags.
L'environnement virtuel doit pointer vers ce dossier.
En plus des dépendances installées dans le conteneur, il faut installer en local pour faire des tests dotenv :
pip install dotenv

Serveur postgresql standalone pour les données métiers :

docker run -d \
    --name postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=mdp \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v postgres-data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres

Pour lister les bonnes versions des bibliothèques à utiliser :
lister_bibliotheques_python.sh