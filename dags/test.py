from dotenv import load_dotenv
import os
from metier.donnees_statiques import test1, test2, test3

os.environ['TEST'] = "oui"
load_dotenv("../.env.dev")

test1()
test2()
test3()
