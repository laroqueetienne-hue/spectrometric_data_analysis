"""
Traitement : moyenne et écart type de l'intensité, pour chaque longueur d'onde.

Principe : on a N spectres (un par fichier .txt). Pour chaque longueur d'onde,
on calcule la moyenne et l'écart type des N valeurs d'intensité.

Produit, dans resultats/<nom_mesure>/ :
  - moyenne_ecart_type.csv  (ouvrable dans Excel)
  - moyenne_ecart_type.png  (graphe : spectre moyen + bande d'écart type)
"""

import matplotlib

matplotlib.use("Agg")  # dessine dans un fichier, sans ouvrir de fenêtre
import matplotlib.pyplot as plt
import numpy as np


def executer(mesure, dossier_resultats):
    """Point d'entrée appelé par main.py.

    mesure : dictionnaire contenant
        mesure["nom"]             -> nom de la mesure
        mesure["longueurs_onde"]  -> tableau 1D (2048 valeurs)
        mesure["intensites"]      -> tableau 2D (nombre de spectres x 2048)
    dossier_resultats : dossier où écrire les résultats
    """
    longueurs_onde = mesure["longueurs_onde"]
    intensites = mesure["intensites"]
    nb_spectres = intensites.shape[0]

    # axis=0 : on calcule "en colonne", donc une valeur par longueur d'onde
    moyenne = intensites.mean(axis=0)
    # ddof=1 : écart type d'échantillon (division par N-1), usage courant en sciences
    ecart_type = intensites.std(axis=0, ddof=1) if nb_spectres > 1 else np.zeros_like(moyenne)

    # --- Fichier CSV (séparateur ; et virgule décimale pour Excel en français) ---
    lignes = ["longueur_onde_nm;moyenne;ecart_type"]
    for lam, moy, ecart in zip(longueurs_onde, moyenne, ecart_type):
        lignes.append(f"{lam:.4f};{moy:.4f};{ecart:.4f}".replace(".", ","))
    (dossier_resultats / "moyenne_ecart_type.csv").write_text("\n".join(lignes), encoding="utf-8-sig")

    # --- Graphe ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(longueurs_onde, moyenne, color="tab:blue", linewidth=1, label="Moyenne")
    ax.fill_between(
        longueurs_onde,
        moyenne - ecart_type,
        moyenne + ecart_type,
        color="tab:blue",
        alpha=0.3,
        label="± 1 écart type",
    )
    ax.set_xlabel("Longueur d'onde (nm)")
    ax.set_ylabel("Intensité (coups)")
    ax.set_title(f"{mesure['nom']} : spectre moyen sur {nb_spectres} spectres")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(dossier_resultats / "moyenne_ecart_type.png", dpi=150)
    plt.close(fig)

    print(f"      -> moyenne_ecart_type.csv et .png écrits ({nb_spectres} spectres)")
