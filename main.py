"""
Script principal : c'est LE fichier à lancer.

    python main.py                 -> utilise config.json
    python main.py autre.json      -> utilise un autre fichier de configuration

Ce qu'il fait :
  1. lit config.json (quelles mesures ? quels traitements ?)
  2. pour chaque mesure, charge les spectres (lecture rapide grâce à la copie)
  3. lance chaque traitement demandé et range les résultats dans resultats/
"""

import importlib
import json
import sys
import traceback
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))  # permet d'importer les dossiers outils/ et traitements/

from outils.lecture import charger_mesure  # noqa: E402


def lire_config():
    nom_config = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    chemin = RACINE / nom_config
    if not chemin.exists():
        sys.exit(f"Fichier de configuration introuvable : {chemin}")
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        sys.exit(
            f"Erreur dans {nom_config} (ligne {erreur.lineno}) : {erreur.msg}\n"
            "Vérifiez les virgules et les guillemets."
        )


def main():
    config = lire_config()

    dossier_brutes = RACINE / config["dossier_donnees_brutes"]
    dossier_converties = RACINE / config["dossier_donnees_converties"]
    dossier_resultats = RACINE / config["dossier_resultats"]

    # Liste vide = toutes les mesures présentes (un sous-dossier = une mesure)
    noms_mesures = config.get("mesures") or sorted(
        d.name for d in dossier_brutes.iterdir() if d.is_dir()
    )
    if not noms_mesures:
        sys.exit(f"Aucune mesure trouvée dans {dossier_brutes} (1 sous-dossier par mesure).")

    noms_traitements = config.get("traitements", [])
    if not noms_traitements:
        sys.exit("Aucun traitement demandé dans config.json (clé \"traitements\").")

    # Chargement des traitements (une erreur ici est signalée avant de commencer)
    traitements = {}
    for nom in noms_traitements:
        try:
            traitements[nom] = importlib.import_module(f"traitements.{nom}")
        except ModuleNotFoundError:
            sys.exit(f"Traitement introuvable : traitements/{nom}.py (vérifiez config.json).")

    for nom_mesure in noms_mesures:
        print(f"\n=== Mesure : {nom_mesure} ===")
        dossier_mesure = dossier_brutes / nom_mesure
        if not dossier_mesure.is_dir():
            print(f"  ! Dossier introuvable : {dossier_mesure} (mesure ignorée)")
            continue

        try:
            mesure = charger_mesure(dossier_mesure, dossier_converties)
        except ValueError as erreur:
            print(f"  ! {erreur} (mesure ignorée)")
            continue

        sortie = dossier_resultats / nom_mesure
        sortie.mkdir(parents=True, exist_ok=True)

        for nom, module in traitements.items():
            print(f"  Traitement : {nom}")
            try:
                module.executer(mesure, sortie)
            except Exception:
                # Un traitement qui plante n'empêche pas les autres de tourner
                print(f"  ! Le traitement '{nom}' a échoué :")
                traceback.print_exc()

    print("\nTerminé. Résultats dans :", dossier_resultats)


if __name__ == "__main__":
    main()
