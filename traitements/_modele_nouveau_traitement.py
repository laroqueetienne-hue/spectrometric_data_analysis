"""
MODÈLE pour créer un nouveau traitement.

Mode d'emploi :
  1. Copiez ce fichier et renommez la copie, par exemple : spectre_maximum.py
     (pas d'espaces ni d'accents dans le nom)
  2. Écrivez votre calcul dans la fonction executer() ci-dessous
  3. Ajoutez le nom du fichier SANS ".py" dans config.json :
         "traitements": ["moyenne_ecart_type", "spectre_maximum"]
  4. Lancez : python main.py
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: F401  (pour faire des graphes)
import numpy as np  # noqa: F401  (pour faire des calculs)


def executer(mesure, dossier_resultats):
    # Ce que vous avez à disposition :
    longueurs_onde = mesure["longueurs_onde"]  # tableau 1D : 2048 valeurs
    intensites = mesure["intensites"]          # tableau 2D : (nb de spectres, 2048)
    # mesure["nom"], mesure["fichiers"], mesure["dates"], mesure["temps_integration"]
    # sont aussi disponibles.

    # --- Écrivez votre calcul ici ---

    # Pour enregistrer un fichier de résultat, utilisez par exemple :
    #   fig.savefig(dossier_resultats / "mon_graphe.png", dpi=150)
    pass
