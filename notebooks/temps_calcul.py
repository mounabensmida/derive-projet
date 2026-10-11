"""Combien de temps chaque méthode met-elle pour traiter une série ?  (temps réel = il faut que ce soit petit)"""
import sys, os, time, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.generateur import generer_serie
from src.residus import residus
from src.methodes import METHODES
import src.detecteurs_stat as stat
import src.detecteur_reseau as reseau

reglages = json.load(open("reglages_semaine4.json"))
series = [residus(generer_serie(seed=900 + i, type_derive="saut_moyenne", intensite=2.0)[0]) for i in range(5)]
print(f"{'méthode':26s} {'ms par série':>14s} {'µs par point':>14s}")
for nom, (f, _) in METHODES.items():
    mesures = []
    for x in series:
        stat._CACHE_P.clear(); reseau._MEMOIRE.clear()        # on vide la mémoire : mesure honnête
        debut = time.perf_counter()
        f(x, reglages[nom])
        mesures.append(time.perf_counter() - debut)
    t = np.median(mesures)
    print(f"{nom:26s} {t * 1000:14.1f} {t / len(series[0]) * 1e6:14.1f}")
print("\nÀ retenir : le réseau doit en plus être ENTRAÎNÉ (compris dans ce temps) ; ensuite, chaque nouveau point coûte très peu.")