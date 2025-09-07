from psycopg2 import sql, connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import os
from datetime import datetime
from .utils import nouveau_curseur


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
