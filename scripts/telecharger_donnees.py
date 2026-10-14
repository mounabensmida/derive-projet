"""Télécharge les 2 fichiers de données réelles (jeu ETT) dans data/. Usage : python scripts/telecharger_donnees.py"""
import os
import urllib.request

BASE = "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/"
DOSSIER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

os.makedirs(DOSSIER, exist_ok=True)
for nom in ("ETTh1.csv", "ETTh2.csv"):
    chemin = os.path.join(DOSSIER, nom)
    if os.path.exists(chemin) and os.path.getsize(chemin) > 1_000_000:
        print("déjà là :", nom)
        continue
    print("téléchargement :", nom, flush=True)
    urllib.request.urlretrieve(BASE + nom, chemin)
print("Données prêtes dans", DOSSIER)