import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from src.generateur import generer_serie, TYPES_DERIVE, evaluer
from src.residus import residus
from src.detecteurs_stat import page_hinkley, cusum, ks_glissant, mw_glissant
from src.calibration import calibrer

P = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6]
METHODES = {
    # nom : (fonction, utiliser_residus, grille de seuils du plus sensible au plus prudent)
    "KS brut":       (lambda s, p: ks_glissant(s, seuil=p), False, P),
    "KS résidus":    (lambda s, p: ks_glissant(s, seuil=p), True,  P),
    "MW résidus":    (lambda s, p: mw_glissant(s, seuil=p), True,  P),
    "PH résidus":    (lambda s, p: page_hinkley(s, seuil=p), True, [10, 15, 20, 25, 30, 40]),
    "CUSUM résidus": (lambda s, p: cusum(s, h=p), True,            [10, 15, 20, 25, 30, 40]),
}

if __name__ == "__main__":
    debut = time.time()
    choix = {}
    for nom, (f, use_res, grille) in METHODES.items():
        print("Calibration :", nom)
        choix[nom] = calibrer(f, grille, utiliser_residus=use_res)
    print("\nSeuils choisis :", choix, "\n")

    lignes = []
    for nom, (f, use_res, _) in METHODES.items():
        for typ in TYPES_DERIVE:
            for seed in range(10):
                s, t0 = generer_serie(seed=seed, type_derive=typ, intensite=2.0)
                x = residus(s) if use_res else s
                r = evaluer(f(x, choix[nom]), t0)
                r.update(methode=nom, type=typ)
                lignes.append(r)
    df = pd.DataFrame(lignes)
    tab = df.groupby(["type", "methode"]).agg(
        detection=("detectee", "mean"), delai=("delai", "mean")).round(2)
    print(tab.unstack("methode")["detection"])
    print()
    print(tab.unstack("methode")["delai"])
    df.to_csv("resultats_semaine2.csv", index=False)
    print(f"\nDurée : {time.time()-debut:.0f} s")