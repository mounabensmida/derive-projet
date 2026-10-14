"""Démo en terminal : une série arrive point par point, le moteur dit quand il alerte.
Exemples :  python notebooks/demo_streaming.py
            python notebooks/demo_streaming.py --derive forme --intensite 2
            python notebooks/demo_streaming.py --source réelle --derive saut_moyenne --intensite 4"""
import sys, os, argparse, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.source import construire_serie, reglages, TYPES
from src.streaming import rejouer

p = argparse.ArgumentParser()
p.add_argument("--source", default="synthétique", choices=["synthétique", "réelle"])
p.add_argument("--derive", default="saut_moyenne", choices=TYPES)
p.add_argument("--intensite", type=float, default=2.0)
p.add_argument("--graine", type=int, default=0)
a = p.parse_args()

serie, t0 = construire_serie(a.source, a.derive, a.intensite, a.graine)
print(f"Série {a.source} : {len(serie)} points, dérive '{a.derive}'" + (f" injectée à t = {t0}" if t0 else " (aucune)"))
vus = set()
NOMS = {"cusum": "CUSUM (niveau)", "reseau": "Autoencodeur (structure)", "controle": "Contrôle sans réseau"}
for r in rejouer(serie, **reglages(a.source)):
    if r["t"] in (672, 1008, 1344):
        print(f"t = {r['t']:4d} : " + {672: "profil appris", 1008: "référence terminée, réseau entraîné", 1344: "validation terminée : la surveillance commence"}[r["t"]])
    for nom in NOMS:
        if r[f"alerte_{nom}"] and nom not in vus:
            vus.add(nom)
            info = f"  (délai {r['t'] - t0} h après la dérive)" if t0 and r["t"] >= t0 else ("  <- FAUSSE ALERTE (avant la dérive)" if t0 else "  <- alerte sur série sans dérive")
            print(f"t = {r['t']:4d} : ALERTE {NOMS[nom]}{info}")
if not vus:
    print("Aucune alerte pendant toute la série.")