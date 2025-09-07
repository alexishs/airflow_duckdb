from psycopg2 import sql, connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import os
from datetime import datetime

bdd_initialisee = False
connexion = None


def en_test() -> bool:
    return os.getenv("TEST") == "oui"


def commit() -> None:
    global connexion
    connexion.commit()


def rollback() -> None:
    global connexion
    connexion.rollback()


def initialiser_bdd(connexion: connection) -> None:
    global bdd_initialisee
    chaine_sql = """
        SELECT count(*) nb_tables
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        """
    curseur = connexion.cursor(cursor_factory=DictCursor)
    curseur.execute(chaine_sql)
    nb_tables = curseur.fetchone()["nb_tables"]
    if nb_tables == 0:
        if en_test():
            chemin_script = "initialisation_base.sql"
        else:
            chemin_script = "/opt/airflow/dags/initialisation_base.sql"
        with open(chemin_script, "r", encoding="utf-8") as script:
            curseur.execute(script.read())
            commit()
    bdd_initialisee = True


def nouveau_curseur() -> cursor:
    global connexion
    global bdd_initialisee
    if not connexion:
        connexion = connect(
            host=os.getenv("PG_METIER_SERVER"),
            dbname=os.getenv("PG_METIER_BASE"),
            user=os.getenv("PG_METIER_USER"),
            password=os.getenv("PG_METIER_PASSWORD"),
        )
    if not bdd_initialisee:
        initialiser_bdd(connexion)
    return connexion.cursor(cursor_factory=DictCursor)


def test1():
    print("passage ds test1")
    curseur = nouveau_curseur()
    curseur.close()
    # if datetime.now().minute % 2 != 0:  # nombre impaire
    #     raise Exception("gros plantage")


def test2():
    curseur = nouveau_curseur()
    curseur.close()
    print("passage ds test2")


def test3():
    curseur = nouveau_curseur()
    curseur.close()
    print("passage ds test3")
