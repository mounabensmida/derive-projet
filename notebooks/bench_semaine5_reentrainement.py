"""Semaine 5, partie 2 : quand réentraîner ? Stratégies comparées sur de VRAIES données (jeu ETT).
Usage :  python notebooks/bench_semaine5_reentrainement.py"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import src.reentrainement as R
from src.donnees_reelles import fenetres_prevision, DEBUTS_TEST

R.PERIODES["tous les 56 j"] = 1344                        # on ajoute une période plus longue
CONDITIONS = [("aucune", 0.0), ("saut", 1.0), ("saut", 3.0), ("relation", 3.0)]
# (stratégie, seuil CUSUM) : plus le seuil est haut, moins on réentraîne
STRATEGIES = [("jamais", None), ("tous les 56 j", None), ("tous les 28 j", None), ("tous les 14 j", None),
            ("tous les 7 j", None), ("sur alerte", 20), ("sur alerte", 50), ("sur alerte", 100),
            ("sur alerte", 200), ("oracle", None)]


def main():
    t0 = time.time()
    fen = [(f, k, XY) for f in ("ETTh1", "ETTh2") for k, XY in enumerate(fenetres_prevision(f, DEBUTS_TEST))]
    lignes = []
    for cond, inten in CONDITIONS:
        for i, (fichier, k, (X, y)) in enumerate(fen):
            sigma = R.sigma_reference(X, y)
            signe = 1 if i % 2 == 0 else -1               # une fenêtre sur deux : dérive vers le bas
            yy = R.injecter(X, y, cond, signe * inten, sigma)
            for strat, h in STRATEGIES:
                e, retr = R.simuler(X, yy, strat, h or 20)
                lignes.append(dict(condition=f"{cond} {inten:g}" if cond != "aucune" else "aucune",
                                fenetre=f"{fichier}-{k}", strategie=strat if h is None else f"{strat} (h={h})",
                                mae=np.nanmean(e[R.T0:]) / sigma, reentrainements=len(retr)))
        print(f"{cond} {inten} fait ({time.time() - t0:.0f} s)", flush=True)
    pd.DataFrame(lignes).to_csv("resultats_semaine5_reentrainement.csv", index=False)
    print("Terminé :", len(lignes), "lignes")


if __name__ == "__main__":
    main()