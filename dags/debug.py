from metier import utils
from metier.utils_bdd import configurer_bdd
from metier.donnees_statiques import telecharger_donnees_statiques, enregistrer_donnees_statiques_en_bdd

utils.definir_en_test()

configurer_bdd()
telecharger_donnees_statiques()
enregistrer_donnees_statiques_en_bdd()
