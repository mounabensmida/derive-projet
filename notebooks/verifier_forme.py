"""Que détecte VRAIMENT le réseau dans la dérive 'forme' ?
Dans notre générateur, 'forme' change DEUX choses à la fois : les queues deviennent lourdes
ET le bruit perd sa mémoire. On les sépare ici."""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.generateur import generer_serie
from src.residus import residus
from src.detecteur_reseau import alertes_reseau
from src.evaluation import garder_zone, evaluer

N, T0, SIGMA = 3360, 1680, 5.0
t = np.arange(N)
PARTIE_REGULIERE = 100 + 20 * np.sin(2 * np.pi * t / 24) + 10 * np.sin(2 * np.pi * t / 168)


def serie_variante(graine, variante):
    s, _ = generer_serie(seed=graine)                  # une série calme
    bruit = s - PARTIE_REGULIERE                       # son bruit seul
    rng = np.random.default_rng(10_000 + graine)
    m = N - T0
    if variante == "blanc_gaussien":                   # pas de queues lourdes, mais PLUS de mémoire
        nouveau = rng.normal(0, SIGMA, m)
    elif variante == "queues_lourdes_avec_memoire":    # queues lourdes, mémoire CONSERVÉE
        e = rng.standard_t(3, m) / np.sqrt(3)
        x = np.zeros(m)
        for i in range(1, m):
            x[i] = 0.6 * x[i - 1] + e[i]
        nouveau = x * SIGMA / x.std()
    else:                                              # "forme" actuelle : queues lourdes ET plus de mémoire
        nouveau = rng.standard_t(3, m) / np.sqrt(3) * SIGMA
    bruit[T0:] = nouveau
    return PARTIE_REGULIERE + bruit


for variante in ["queues_lourdes_sans_memoire", "queues_lourdes_avec_memoire", "blanc_gaussien"]:
    reussi = {"Autoencodeur": [], "Sans réseau": []}
    for graine in range(60):
        x = residus(serie_variante(graine, variante))
        for nom, avec_reseau in [("Autoencodeur", True), ("Sans réseau", False)]:
            r = evaluer(garder_zone(alertes_reseau(x, 1.5, avec_reseau)), T0)
            reussi[nom].append(r["detectee"] and r["fausses_alertes"] == 0)
    print(f"{variante:30s}", {k: f"{np.mean(v):.0%}" for k, v in reussi.items()})