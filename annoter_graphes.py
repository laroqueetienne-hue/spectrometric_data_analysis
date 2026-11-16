"""Recrée les graphes moyens avec les principales raies spectrales annotées.

Usage :
    python annoter_graphes.py [config.json]

Les fichiers moyenne_ecart_type_annotee.png sont écrits à côté des CSV ;
les graphes originaux ne sont pas modifiés.
"""

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

RACINE = Path(__file__).resolve().parent

RAIES = (
    (486.1, "Hβ 486,1 nm", "hydrogene", 3.0),
    (500.5, "N I 500,5 nm", "air", 3.0),
    (518.0, "N II ~518 nm", "air", 3.0),
    (532.0, "Laser Nd:YAG 532 nm (doublet)", "laser", 3.0),
    (568.0, "N I 568,0 nm", "air", 3.0),
    (594.2, "N I 594,2 nm", "air", 3.0),
    (656.3, "Hα 656,3 nm (élargie par effet Stark)", "hydrogene", 4.0),
    (746.8, "N I 746,8 nm", "air", 3.0),
    (777.4, "O I 777,4 nm (triplet)", "air", 4.0),
    (822.5, "N I 821-824 nm", "air", 4.0),
    (844.6, "O I / N I 844,6 nm", "air", 3.0),
    (868.0, "N I 868,0 nm", "air", 3.0),
    (930.0, "2e ordre (2 x 465 nm)", "ordre2", 4.0),
    (972.0, "2e ordre (2 x 486 nm)", "ordre2", 4.0),
    (1002.0, "2e ordre N II (2 x 501 nm)", "ordre2", 4.0),
    (1064.0, "Laser 1064 nm + 2e ordre 532 nm", "laser", 4.0),
)

COULEURS = {
    "hydrogene": "red",
    "air": "forestgreen",
    "laser": "blueviolet",
    "ordre2": "dimgray",
}


def _lire_csv(chemin):
    with chemin.open(encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=";")
        colonnes = {"longueur_onde_nm", "moyenne", "ecart_type"}
        if not lecteur.fieldnames or not colonnes.issubset(lecteur.fieldnames):
            raise ValueError(f"Colonnes manquantes dans {chemin}")

        longueurs_onde = []
        moyenne = []
        ecart_type = []
        for numero, ligne in enumerate(lecteur, start=2):
            try:
                valeurs = [
                    float(ligne[nom].replace(",", "."))
                    for nom in ("longueur_onde_nm", "moyenne", "ecart_type")
                ]
            except (AttributeError, TypeError, ValueError) as erreur:
                raise ValueError(f"Valeur invalide dans {chemin}, ligne {numero}") from erreur
            if not all(math.isfinite(valeur) for valeur in valeurs):
                raise ValueError(f"Valeur non finie dans {chemin}, ligne {numero}")
            longueur, intensite, ecart = valeurs
            if ecart < 0:
                raise ValueError(f"Écart type négatif dans {chemin}, ligne {numero}")
            longueurs_onde.append(longueur)
            moyenne.append(intensite)
            ecart_type.append(ecart)

    if len(longueurs_onde) < 2:
        raise ValueError(f"Pas assez de points pour tracer {chemin}")
    if any(b <= a for a, b in zip(longueurs_onde, longueurs_onde[1:])):
        raise ValueError(f"Les longueurs d'onde ne sont pas croissantes dans {chemin}")

    return (
        np.asarray(longueurs_onde),
        np.asarray(moyenne),
        np.asarray(ecart_type),
    )


def _annoter_csv(chemin_csv):
    longueurs_onde, moyenne, ecart_type = _lire_csv(chemin_csv)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.plot(longueurs_onde, moyenne, color="tab:blue", linewidth=1, label="Moyenne")
    ax.fill_between(
        longueurs_onde,
        moyenne - ecart_type,
        moyenne + ecart_type,
        color="tab:blue",
        alpha=0.3,
        label="± 1 écart type",
    )

    for longueur_ref, etiquette, categorie, fenetre in RAIES:
        if not longueurs_onde[0] <= longueur_ref <= longueurs_onde[-1]:
            continue
        indices = np.flatnonzero(np.abs(longueurs_onde - longueur_ref) <= fenetre)
        if indices.size == 0:
            continue
        indice_pic = indices[np.argmax(moyenne[indices])]
        x_pic = longueurs_onde[indice_pic]
        y_pic = moyenne[indice_pic]
        ax.annotate(
            etiquette,
            xy=(x_pic, y_pic),
            xytext=(0, 28),
            textcoords="offset points",
            ha="center",
            va="bottom",
            rotation=90,
            rotation_mode="anchor",
            color=COULEURS[categorie],
            fontsize=7,
            arrowprops={"arrowstyle": "-", "color": COULEURS[categorie], "linewidth": 0.8},
            annotation_clip=False,
        )

    categories = [
        ("Hydrogène (série de Balmer)", "hydrogene"),
        ("Azote / oxygène de l'air (plasma)", "air"),
        ("Laser (Nd:YAG)", "laser"),
        ("Second ordre du réseau", "ordre2"),
    ]
    legende_raies = [
        Line2D([0], [0], color=COULEURS[categorie], linewidth=2, label=nom)
        for nom, categorie in categories
    ]
    legende_spectre = ax.legend(loc="upper right")
    ax.add_artist(legende_spectre)
    ax.legend(
        handles=legende_raies,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=2,
        fontsize=8,
        frameon=False,
    )
    ax.set_xlabel("Longueur d'onde (nm)")
    ax.set_ylabel("Intensité (coups)")
    ax.set_title(chemin_csv.parent.name + " : spectre moyen annoté")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    sortie = chemin_csv.with_name("moyenne_ecart_type_annotee.png")
    fig.savefig(sortie, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  Graphe annoté : {sortie}")


def main():
    nom_config = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    chemin_config = RACINE / nom_config
    if not chemin_config.is_file():
        sys.exit(f"Fichier de configuration introuvable : {chemin_config}")
    try:
        config = json.loads(chemin_config.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        sys.exit(f"Erreur dans {nom_config} (ligne {erreur.lineno}) : {erreur.msg}")

    dossier_resultats = RACINE / config["dossier_resultats"]
    if not dossier_resultats.is_dir():
        sys.exit(f"Dossier de résultats introuvable : {dossier_resultats}")

    fichiers_csv = sorted(dossier_resultats.rglob("moyenne_ecart_type.csv"))
    if not fichiers_csv:
        sys.exit(f"Aucun fichier moyenne_ecart_type.csv dans {dossier_resultats}")

    print(f"Annotation de {len(fichiers_csv)} graphe(s)...")
    for chemin_csv in fichiers_csv:
        _annoter_csv(chemin_csv)


if __name__ == "__main__":
    main()
