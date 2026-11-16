"""
Lecture des fichiers .txt du spectromètre.

Ce fichier contient toute la partie "technique" : il sait lire un fichier .txt,
et regrouper tous les fichiers d'une mesure dans un seul tableau de nombres.

Si un jour le format des fichiers change, c'est CE fichier (et lui seul)
qu'il faudra adapter.
"""

from datetime import datetime
from pathlib import Path

import numpy as np

# Ligne qui sépare l'en-tête (infos) des données (nombres)
MARQUEUR_DEBUT_DONNEES = ">>>>>Begin Spectral Data<<<<<"


def _lire_date(entete):
    """Lit la ligne 'Date: Fri Oct 30 13:42:47 CET 2026' et renvoie un texte
    au format 2026-10-30 13:42:47. Renvoie '' si la ligne est absente ou illisible."""
    for ligne in entete.splitlines():
        if ligne.startswith("Date:"):
            morceaux = ligne.replace("Date:", "").split()
            try:
                # morceaux = ['Fri', 'Oct', '30', '13:42:47', 'CET', '2026']
                date = datetime.strptime(
                    f"{morceaux[1]} {morceaux[2]} {morceaux[3]} {morceaux[5]}",
                    "%b %d %H:%M:%S %Y",
                )
                return date.strftime("%Y-%m-%d %H:%M:%S")
            except (IndexError, ValueError):
                return ""
    return ""


def _lire_temps_integration(entete):
    """Lit la ligne 'Integration Time (sec): 1,000000E-1' (virgule décimale).
    Renvoie un nombre, ou 'nan' (= "pas un nombre") si introuvable."""
    for ligne in entete.splitlines():
        if ligne.startswith("Integration Time"):
            valeur = ligne.split(":", 1)[1].strip().replace(",", ".")
            try:
                return float(valeur)
            except ValueError:
                return float("nan")
    return float("nan")


def lire_fichier(chemin):
    """Lit UN fichier .txt et renvoie :
    (longueurs d'onde, intensités, date, temps d'intégration)."""
    texte = Path(chemin).read_text(encoding="utf-8", errors="replace")

    if MARQUEUR_DEBUT_DONNEES not in texte:
        raise ValueError(f"Marqueur de début de données introuvable dans {chemin}")

    entete, donnees = texte.split(MARQUEUR_DEBUT_DONNEES, 1)

    # Les nombres utilisent la virgule comme séparateur décimal (ex : 440,321).
    # On la remplace par un point, puis on convertit tout le bloc d'un coup.
    try:
        nombres = np.array(donnees.replace(",", ".").split(), dtype=float)
    except ValueError:
        raise ValueError(f"Données illisibles dans {chemin}") from None

    if nombres.size == 0 or nombres.size % 2 != 0:
        raise ValueError(f"Données illisibles dans {chemin}")

    # Une ligne = 2 nombres : longueur d'onde, intensité
    nombres = nombres.reshape(-1, 2)
    return nombres[:, 0], nombres[:, 1], _lire_date(entete), _lire_temps_integration(entete)


def _convertir_dossier(dossier_mesure, fichiers_txt):
    """Lit tous les .txt d'une mesure et les empile dans un grand tableau."""
    longueurs_onde_ref = None
    liste_intensites, noms, dates, temps = [], [], [], []

    for i, fichier in enumerate(fichiers_txt, start=1):
        try:
            lam, inten, date, tint = lire_fichier(fichier)
        except ValueError as erreur:
            print(f"    ! Fichier ignoré : {erreur}")
            continue

        if longueurs_onde_ref is None:
            longueurs_onde_ref = lam
        elif lam.shape != longueurs_onde_ref.shape or not np.allclose(
            lam, longueurs_onde_ref, atol=1e-3
        ):
            # Axe différent des autres fichiers : on ne peut pas les comparer
            print(f"    ! Fichier ignoré (axe de longueurs d'onde différent) : {fichier.name}")
            continue

        liste_intensites.append(inten)
        noms.append(fichier.name)
        dates.append(date)
        temps.append(tint)

        if i % 200 == 0:
            print(f"    ... {i}/{len(fichiers_txt)} fichiers lus")

    if not liste_intensites:
        raise ValueError(f"Aucun fichier lisible dans {dossier_mesure}")

    return {
        "longueurs_onde": longueurs_onde_ref,
        "intensites": np.vstack(liste_intensites),  # 1 ligne par fichier
        "fichiers": np.array(noms),
        "dates": np.array(dates),
        "temps_integration": np.array(temps),
    }


def charger_mesure(dossier_mesure, dossier_converties):
    """Renvoie les données d'une mesure (= un dossier de fichiers .txt).

    - 1re fois : lit tous les .txt (lent) et sauvegarde une copie rapide
      dans donnees/converties/<nom_mesure>.npz
    - Fois suivantes : relit directement la copie (quasi instantané),
      sauf si des fichiers .txt ont été ajoutés, retirés ou modifiés.
    """
    dossier_mesure = Path(dossier_mesure)
    dossier_converties = Path(dossier_converties)
    dossier_converties.mkdir(parents=True, exist_ok=True)

    fichiers_txt = sorted(dossier_mesure.glob("*.txt"))
    if not fichiers_txt:
        raise ValueError(f"Aucun fichier .txt dans {dossier_mesure}")

    copie = dossier_converties / f"{dossier_mesure.name}.npz"

    # La copie rapide est-elle encore valable ?
    if copie.exists():
        plus_recent_txt = max(f.stat().st_mtime for f in fichiers_txt)
        if copie.stat().st_mtime >= plus_recent_txt:
            contenu = np.load(copie, allow_pickle=False)
            mesure = {cle: contenu[cle] for cle in contenu.files}
            # Valable si elle a vu exactement le même nombre de fichiers .txt
            if int(mesure["nb_fichiers_txt"]) == len(fichiers_txt):
                print(f"    Copie rapide utilisée ({len(mesure['fichiers'])} spectres)")
                mesure["nom"] = dossier_mesure.name
                return mesure

    print(f"    Lecture de {len(fichiers_txt)} fichiers .txt (un peu long)...")
    mesure = _convertir_dossier(dossier_mesure, fichiers_txt)
    mesure["nb_fichiers_txt"] = np.array(len(fichiers_txt))
    np.savez_compressed(copie, **mesure)
    mesure["nom"] = dossier_mesure.name
    return mesure
