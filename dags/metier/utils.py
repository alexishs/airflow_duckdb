from __future__ import annotations
import os
from dotenv import load_dotenv
import logging

def definir_en_test()-> None:
    os.environ['TEST'] = str(True)
    load_dotenv("../.env.dev")

def en_test() -> bool:
    return os.getenv("TEST") == str(True)

def log_infos_compagnie(compagnie: dict, message: str)-> None:
    print(f"Compagnie {compagnie['id_compagnie']} : {message}")
    #print("Compagnie " + compagnie["id_compagnie"] + " : " + message)

def log_warning_compagnie(compagnie: dict, message: str)-> None:
    logging.warning(f"Compagnie {compagnie['id_compagnie']} : {message}")

def chemin_base(chemin_contenu: str)-> str:
    if en_test():
        return "../" + chemin_contenu
    else:
        return "/opt/airflow/" + chemin_contenu

def chemin_dags(chemin_contenu: str)-> str:
    if en_test():
        return "./" + chemin_contenu
    else:
        return "/opt/airflow/dags/" + chemin_contenu

def chemin_cache_metier(chemin_contenu: str):
    return chemin_base("cache_metier/" + chemin_contenu)

def chemin_cache_compagnie(compagnie: dict, chemin_contenu: str)-> str:
    return chemin_cache_metier(f"comp_{compagnie['id_compagnie']}/{chemin_contenu}")