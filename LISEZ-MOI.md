# Projet d'analyse de spectres

Ce projet lit des fichiers .txt de spectromètre, calcule la moyenne et l'écart
type de l'intensité pour chaque longueur d'onde, et produit un graphe et un
tableau (ouvrable dans Excel) par mesure.

## 1. Installation (une seule fois)

1. Installer Python 3.10 ou plus récent (https://www.python.org/downloads/).
   Sous Windows, cocher « Add Python to PATH » pendant l'installation.
2. Ouvrir un terminal dans le dossier du projet et taper :

       pip install -r requirements.txt

## 2. Organisation des dossiers

    projet_spectres/
    ├── config.json              réglages : quelles mesures, quels traitements
    ├── main.py                  le fichier à lancer
    ├── donnees/
    │   ├── brutes/              VOS .txt : un sous-dossier par mesure
    │   └── converties/          copies rapides créées automatiquement
    ├── outils/lecture.py        sait lire les .txt du spectromètre
    ├── traitements/             un fichier = un calcul
    └── resultats/               graphes et tableaux produits

## 3. Utilisation au quotidien

1. Créez un sous-dossier par mesure dans `donnees/brutes/`
   (ex. `donnees/brutes/mesure_air/`) et déposez-y les fichiers .txt.
2. Lancez dans le terminal :

       python main.py

3. Récupérez les résultats dans `resultats/<nom_de_la_mesure>/`.

La première fois, la lecture des .txt prend un peu de temps. Ensuite le
programme utilise une copie rapide (dans `donnees/converties/`). Si vous
ajoutez, retirez ou modifiez des .txt, la copie est refaite automatiquement.
Vous pouvez supprimer le dossier `converties` sans risque : il se recrée.

## 4. Le fichier config.json

    {
      "dossier_donnees_brutes": "donnees/brutes",
      "dossier_donnees_converties": "donnees/converties",
      "dossier_resultats": "resultats",
      "mesures": [],
      "traitements": ["moyenne_ecart_type"]
    }

- `mesures` : liste vide = toutes les mesures présentes. Pour en choisir
  quelques-unes : `["mesure_air", "mesure_h2"]`.
- `traitements` : noms des fichiers de `traitements/`, sans le `.py`.
- Attention : chaque élément d'une liste est entouré de guillemets et séparé
  par une virgule, sauf le dernier. Une virgule oubliée provoque une erreur.
- Pour tester un autre réglage sans toucher à l'original :
  copiez `config.json` en `config_test.json`, puis `python main.py config_test.json`.

## 5. Ajouter un nouveau traitement

1. Copiez `traitements/_modele_nouveau_traitement.py` et renommez la copie
   (ex. `spectre_maximum.py`, sans espace ni accent).
2. Écrivez votre calcul dans la fonction `executer`.
3. Ajoutez `"spectre_maximum"` à la liste `traitements` de `config.json`.
4. Lancez `python main.py`.

Chaque traitement reçoit les spectres sous la forme d'un tableau
`mesure["intensites"]` (une ligne par fichier, une colonne par longueur d'onde)
et l'axe `mesure["longueurs_onde"]`. Si un traitement plante, les autres
continuent.

## 6. Ajouter de nouvelles données

Ajoutez simplement des .txt dans un sous-dossier existant, ou créez un nouveau
sous-dossier pour une nouvelle mesure. Rien d'autre à modifier.

## 7. Problèmes fréquents

- « Fichier ignoré (axe de longueurs d'onde différent) » : ce spectre n'a pas
  la même calibration que les autres de sa mesure, il est exclu du calcul.
- « Marqueur de début de données introuvable » : le fichier n'a pas le format
  attendu (ligne `>>>>>Begin Spectral Data<<<<<`).
- Toute modification du format des .txt se règle uniquement dans
  `outils/lecture.py`.
