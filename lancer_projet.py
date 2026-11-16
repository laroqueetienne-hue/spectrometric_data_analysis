"""Lance l'analyse des données puis l'annotation des graphes.

Usage :
    python lancer_projet.py
    python lancer_projet.py autre_config.json
"""

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent


def main():
    commandes = (
        [sys.executable, str(RACINE / "main.py"), *sys.argv[1:]],
        [sys.executable, str(RACINE / "annoter_graphes.py"), *sys.argv[1:]],
    )
    for commande in commandes:
        subprocess.run(commande, cwd=RACINE, check=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as erreur:
        sys.exit(f"Échec de la commande {Path(erreur.cmd[1]).name} (code {erreur.returncode}).")
