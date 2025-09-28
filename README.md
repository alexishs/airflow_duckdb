# Pipelines GTFS/GTFS-RT

*Ce projet est un TP réalisé dans le cadre d'une formation.*

## Objectif
Enregistrer les données des transports en commun et les mettre à disposition des outils de dashboarding (pour affichage des KPI, retards, position des véhicules…).

Le développement est effectué à partir des données de Lignes d'Azure, la compagnie de transport en commun de l'agglomération de Nice. Il est possible de configurer plusieurs compagnies de transport.

## Méthode abordée :
Pipelines (ETL) en pythons exécutés dans Airflow avec enregistrement des données dans une base PostgreSQL.
Conteneurs Docker pour l'installation/configuration de Airflow (avec utilisation d'un serveur PostgreSQL comme metastore). La configuration du serveur PostgreSQL hébergeant la base de données métier et des outils de dashboarding n'est pas abordée dans ce projet.

## Pré-requis
**Ce projet a été développé sous Linux (Ubuntu 24.04 LTS). Les instructions présentées ci-après supposent une installation sous cet environnement.**
Un environnement Docker doit être installé et un serveur PostgreSQL pour les données métier doit être disponible.

## Structure

```bash
 ├── .env.dev
 ├── .git
 ├── .gitignore
 ├── airflow_dev.Dockerfile
 ├── cache_metier # Dossier dans lequel les fichiers temporaires des pipelines sont stockés
 ├── compose_dev.yaml
 ├── config_pgadmin_dev.json
 ├── creation_tables.py
 ├── creer_demarrer_conteneurs_dev.sh 
 ├── dags
 │  ├── .airflowignore
 │  ├── .venv
 │  ├── __init__.py
 │  ├── dag_donnees_rt.py
 │  ├── dag_donnees_statiques.py
 │  ├── debug.py # fichier à exécuter en local (hors Docker) pour développement/débogage
 │  ├── initialisation_base.sql
 │  └── metier # Dossier contenant le code source des pipelines
 ├── generer_cles_secretes.py
 ├── LICENSE
 ├── lister_bibliotheques_python.sh
 ├── logs # Dossier contenant les logs générés par Airflow
 ├── README.md
 ├── requirements.txt # Contient les bibliothèques Python à installer pour développement local (en dehors de Airflow)
 ├── supprimer_conteneurs_dev.sh
 ├── tout_reinitialiser.sh
```

## Configuration

### Fichier .env.dev
Créer un fichier .env.dev avec les variables suivantes :

```yaml
# PostgreSQL (utilisé comme metastore interne à Airflow)
# Ce service est créé et géré avec un conteneur Docker.
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# pgAdmin
# Ce service est créé et géré avec un conteneur Docker.
# Il permet de se connecter au metastore de Airflow en cas de besoin
# (serveur PostgreSQL paramétré ci-avant)
PGADMIN_DEFAULT_EMAIL=
PGADMIN_DEFAULT_PASSWORD=

# Airflow
# Ce service est créé et géré avec Docker (un conteneur "Webservice" et un autre "Scheduler").
# Les variables AIRFLOW__CORE__FERNET_KEY et AIRFLOW__WEBSERVER__SECRET_KEY peuvent être renseignées
# avec le script python generer_cles_secretes.py (voir section Exécution en local/Débogage)
# La variable AIRFLOW_UID doit être renseignée avec l'UID utilisé pour gérer les fichiers générés par Airflow
# sur l'hôte (partage de répertoire entre la machine hôte et Docker). Dans un environnement de développement,
# il s'agit de l'UID de l'utilisateur du développeur. Pour connaître son UID, exécuter la commande "id -u".
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@airflow_postgres_dev:5432/${POSTGRES_DB}
AIRFLOW__CORE__FERNET_KEY=
AIRFLOW__WEBSERVER__SECRET_KEY=
AIR_FLOW_USER_NAME=
AIR_FLOW_USER_PASSWORD=
AIR_FLOW_USER_FIRST_NAME=
AIR_FLOW_USER_LAST_NAME=
AIR_FLOW_USER_EMAIL=
AIRFLOW_UID=

# Base métier
PG_METIER_USER=
PG_METIER_PASSWORD=
PG_METIER_SERVER=
PG_METIER_BASE=

# Services par défaut GTFS
# Si plusieurs compagnies, séparer les valeurs par des points-virgule.
# ces informations sont utilisées à la création des tables de la base métier.
# Des compagnies supplémentaires peuvent par la suite être ajoutées dans la table "compagnie".
GTFS_LIBELLES="Nice Côte d'Azur"
GTFS_URLS_INFOS_STATIQUES="https://chouette.enroute.mobi/api/v1/datas/OpendataRLA/gtfs.zip"
GTFS_URLS_RT="https://www.data.gouv.fr/api/1/datasets/r/af3f0734-ef07-468e-b8c9-aed97e4c8a32"
```

### Fichier config_pgadmin_dev.json
Fichier à créer pour la configuration du service PGAdmin.
Les valeurs pour Username et MaintenanceDB doivent correspondre aux variables POSTGRES_USER et POSTGRES_DB.
Le mot de passe correspond à la valeur de la variable POSTGRES_PASSWORD.

```json
{
    "Servers": {
        "1": {
            "Name": "PostgreSQL Service",
            "Group": "Docker Servers",
            "Port": 5432,
            "Username": "mettre la même valeur que la variable POSTGRES_USER",
            "Host": "airflow_postgres_dev",
            "SSLMode": "prefer",
            "MaintenanceDB": "mettre la même valeur que la variable POSTGRES_DB"
        }
    }
}
```


## Installation Airflow avec Docker

```bash
creer_demmarrer_conteneurs_dev.sh
```

Liste des ports par services créés et accessibles en HTTP :

- 8080 : Console d'administration d'Airflow avec ses DAGs ;
- 8081 : PGAdmin (si besoin d'accès au Metastore d'Airflow)

## Exécution en local/Débogage

Il est possible d'exécuter/déboger en local le code métier utilisé par les DAGs.

Le développement s'effectue dans le dossier "dags".

### création de l'environnement virtuel :

```bash
# on se déplace dans le sous-dossier dags
cd ./dags
# on crée le répertoire caché de l'environnement (avec utilisation du module venv)
python -m venv .venv
# on active l'environnement
source .venv/bin/activate
# Installation des librairies nécessaire pour une exécution locale en dehors d'Airflow
pip install -r ../requirements.txt
```

Le fichier requirements.txt a été généré à partir des versions exactes des bibliothèques utilisées par Airflow dans ses conteneurs Docker.
Il est possible de lister les bibliothèques installées dans les conteneurs avec le script lister_bibliotheques_pyton.sh

### Débogage dans VSCode

Exemple de fichier de configuration (launch.json) pour déboger :

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Fichier test.py",
            "type": "debugpy",
            "request": "launch",
            "cwd": "${workspaceFolder}/dags",
            "program": "debug.py",
            "console": "integratedTerminal"
        }
    ]
}
```

## Observations diverses sur le développement

### Difficultés rencontrées
- Configuration des conteneurs d'Airflow avec la gestion des droits sur les répertoire locaux mappés vers les conteneurs (gestion UID)
- Pbs de compatibilité entre les versions de Python entre le développement local et l'exécution dans les conteneurs Docker. L'exécution en local n'était pas demandé, mais c'est pour moi un pré-requis obligatoire car je ne me vois pas travailler sur de gros projets sans pouvoir développer avec debugger en local. Je n'ai pas eu le temps de creuser l'exécution des DAGs dans Airflow tout en utilisant un debugger dans l'IDE.
- Pandas.to_sql() fonctionne très bien pour "exporter" un Dataframe en BDD, mais n'est pas adapté en l'état pour gérer les opérations CREATE/UPDATE/UPSERT dans des tables déjà existantes (voir ci-dessous).
- Pbs de choix et de configuration/prise en main de l'outil de dashboarding sur la fin du projet (Apache Superset). J'aurais mieux fait de choisir Dash (théoriquement plus long à mettre en place, mais ça aurait certainement mieux fonctionné).

### Avancement
L'accent a été mis sur la structuration des données et je n'ai pas eu le temps d'effectuer la gestion du positionnement GPS et les tableaux de bord dans un délai relativement court vues les problématiques rencontrées.

Les données ingérées sont nettoyées, correctement typées et directement exploitables en SQL pour la génération des statistiques et tableaux de bord. Les logs permettent une vue sur le traitement des données avant importation en BDD.

### Structuration de l'enregistrement des données :
Développement d'une classe d'abstraction des opérations CRUD SQL avec prise en compte optionnelle des Dataframe Pandas (classe dags/metier/connexion_bdd/ConnexionBDD et classe orientée métier dags/metier/utils_bdd/ConnexionBDDMetier) avec gestion des INSERT, UPDATE et UPSERT.

#### Pandas
Pandas.to_sql() permet un export en SQL d'un Dataframe, mais ne permet pas, en l'état, d'exporter les données dans une BDD existante en respectant la structure des tables et la gestion de la pré-existance des données à enregistrer en table.

Pour palier à ces inconvénients, les Dataframes Pandas sont pris en charge avec des fonctionalités de formatage des colonnes à partir des types de champs de la table liée et la gestion des INSERT/UPDATE/UPSERT s'effectue en utilisant la fonction pandas.to_sql() lorsque cela est possible.
Cette possibilité dépend du type d'opération demandée et des contraintes d'intégrité des champs de la table liée (méthodes ConnexionBDD.appliquer_types_champs_dans_df et ConnexionBDD.enregistrer_df_dans_table). 

Honnêtement, j'ai du mal à croire qu'il n'y ait aucune fonctionalité/bibliothèque déjà existante qui ne fasse déjà ce travail. Mais l'implémenter moi-même a été formateur.

### Exemple de requête utilisable dans un dashboard

Décalage moyen, sur la journée en cours et pour la 1ère compagnie (Nice), par horaires d'arrivées prévues, entre les horaires d'arrivées prévues et les horaires d'arrivées calculées (effectives pour les horaires passées et prédictives pour les horaires à venir), en respectant les différences de timezones prévues dans GTFS :

*Note : la requête prend en compte la timezone exhaustive pour chaque arrêt, mais il est possible de la simplifier, considérant qu'une seule timezone est applicable pour la compagnie visée (Nice).
Une évolution possible serait d'enregistrer dans la table stop_times la timezone calculée pour alléger le traitement de recherche de timezone.*

```sql
with stop_times_tz as (
	select
		stop_times.id_compagnie,
		stop_times.trip_id,
		stop_times.stop_id,
		stop_times.arrival_time,
		coalesce(stops.stop_timezone, coalesce(stop_parent.stop_timezone, agency.agency_timezone)) calc_time_zone
	from
		stop_times
		inner join stops
			on stops.id_compagnie = stop_times.id_compagnie
			and stops.stop_id = stop_times.stop_id
		left outer join stops stop_parent
			on stop_parent.id_compagnie = stops.id_compagnie
			and stop_parent.stop_id  = stops.parent_station
		inner join trips
			on trips.id_compagnie = stop_times.id_compagnie
			and trips.trip_id  = stop_times.trip_id 
		inner join routes
			on routes.id_compagnie = trips.id_compagnie
			and routes.route_id = trips.route_id
		inner join agency
			on agency.id_compagnie = routes.id_compagnie
			and agency.agency_id = routes.agency_id 
)
select 
	stop_times_tz.arrival_time,
	rt_trip_update.arrival AT TIME ZONE 'UTC' AT TIME ZONE stop_times_tz.calc_time_zone as arrivee_calculee,
	cast(stop_times_tz.arrival_time as time) - cast((rt_trip_update.arrival AT TIME ZONE 'UTC' AT TIME ZONE stop_times_tz.calc_time_zone) as time) difference_moyenne,
	rt_trip_update.trip_id 
from
	rt_trip_update
	inner join stop_times_tz
		on stop_times_tz.id_compagnie = rt_trip_update.id_compagnie 
		and stop_times_tz.trip_id = rt_trip_update.trip_id
		and stop_times_tz.stop_id = rt_trip_update.stop_id
where
	rt_trip_update.id_compagnie = 1
	and rt_trip_update.arrival between cast(now() as date) and cast(now() as date) + cast('23:59:59' as time)
order by
	stop_times_tz.arrival_time;
```