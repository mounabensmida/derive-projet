"""Semaine 5 : lire les résultats de détection sur données réelles.
Usage :  python notebooks/analyse_semaine5_detection.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from src.statistiques import intervalle_wilson

d = pd.read_csv("resultats_semaine5_detection.csv")
ORDRE = ["CUSUM", "Page-Hinkley", "KS", "Mann-Whitney", "Autoencodeur", "Sans réseau (contrôle)"]
inj = d[d["type"] != "calme"].copy()
inj["detectee"] = inj["detectee"].astype(bool)

print("\n=== TABLEAU 1 : % de dérives détectées (détection propre), fenêtres du FUTUR ===")
t1 = inj.pivot_table(index=["type", "intensite"], columns="methode", values="detectee", aggfunc="mean")[ORDRE] * 100
print(t1.round(0).astype(int).to_string())

print("\n=== TABLEAU 2 : moyenne par type de dérive (3 intensités regroupées), avec fourchette à 95 % ===")
lignes = {}
for typ, g in inj.groupby("type"):
    lignes[typ] = {}
    for m in ORDRE:
        gm = g[g["methode"] == m]
        s, n = int(gm["detectee"].sum()), len(gm)
        lo, hi = intervalle_wilson(s, n)
        lignes[typ][m] = f"{s / n:.0%} [{lo:.0%}-{hi:.0%}]"
print(pd.DataFrame(lignes).T[ORDRE].to_string())

print("\n=== TABLEAU 3 : délai médian (heures) des dérives détectées ===")
print(inj[inj["detectee"]].pivot_table(index="type", columns="methode", values="delai", aggfunc="median")[ORDRE].round(0).to_string())

calme = d[d["type"] == "calme"]
print("\n=== TABLEAU 4 : séries NON modifiées du futur (27 fenêtres) ===")
t4 = calme.groupby("methode").agg(avant=("alerte_avant", "mean"), episodes=("episodes", "sum"), heures=("heures", "sum")).loc[ORDRE]
t4["avec alerte avant t0"] = (t4["avant"] * 100).round(0).astype(int).astype(str) + "%"
t4["épisodes / 1000 h"] = (t4["episodes"] / t4["heures"] * 1000).round(2)
print(t4[["avec alerte avant t0", "épisodes / 1000 h"]].to_string())
print("(calibration visée : 20 % des fenêtres du passé)")