"""Semaine 5, partie 1 : les 6 détecteurs sur de VRAIES séries (jeu ETT), avec dérives injectées.
Usage :  python notebooks/bench_semaine5_detection.py"""
import sys, os, json, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from src.donnees_reelles import fenetres_detection, DEBUTS_CALIBRATION, DEBUTS_TEST
from src.injection import injecter, TYPES_INJECTES, T0
from src.evaluation import evaluer, garder_zone, episodes, ZONE_JUGEMENT
from src.residus import residus
from src.detecteurs_stat import page_hinkley, cusum, ks_glissant, mw_glissant
from src.detecteur_reseau import alertes_reseau

INTENSITES = [2.0, 4.0, 6.0]           # en écarts-types de la série réelle
CIBLE = 0.20                           # on accepte 20 % de fenêtres avec alerte (les vraies séries bougent toutes seules)
FICHIER_REGLAGES = "reglages_semaine5.json"

# Sur des données réelles les seuils doivent être BEAUCOUP plus hauts qu'en synthétique : grilles étendues
GRILLE_H = [20, 35, 50, 80, 120, 200, 300, 500]
GRILLE_P = [1e-5, 1e-8, 1e-12, 1e-16, 1e-20, 1e-30, 1e-50]
GRILLE_MARGE = [1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]
METHODES = {
    "CUSUM":                  (lambda x, r: cusum(x, h=r), GRILLE_H),
    "Page-Hinkley":           (lambda x, r: page_hinkley(x, seuil=r), GRILLE_H),
    "KS":                     (lambda x, r: ks_glissant(x, seuil=r), GRILLE_P),
    "Mann-Whitney":           (lambda x, r: mw_glissant(x, seuil=r), GRILLE_P),
    "Autoencodeur":           (lambda x, r: alertes_reseau(x, r, True), GRILLE_MARGE),
    "Sans réseau (contrôle)": (lambda x, r: alertes_reseau(x, r, False), GRILLE_MARGE),
}


def calibrer_reel():
    """Règle les seuils sur les fenêtres du PASSÉ (heures 0 à 6720), sans dérive injectée."""
    fen = fenetres_detection("ETTh1", DEBUTS_CALIBRATION)
    X = [residus(w[:T0]) for _, w in fen]
    reglages = {}
    for nom, (f, grille) in METHODES.items():
        reglages[nom] = grille[-1]
        for g in grille:
            taux = np.mean([len(garder_zone(f(x, g))) > 0 for x in X])
            print(f"  {nom:24s} seuil {g}: {taux:.0%} des fenêtres avec alerte", flush=True)
            if taux <= CIBLE:
                reglages[nom] = g
                break
    json.dump(reglages, open(FICHIER_REGLAGES, "w"), indent=1)
    return reglages


def main():
    t_debut = time.time()
    if os.path.exists(FICHIER_REGLAGES):
        reglages = json.load(open(FICHIER_REGLAGES)); print("Réglages relus :", reglages)
    else:
        reglages = calibrer_reel(); print("Réglages :", reglages)
    fen = fenetres_detection("ETTh1", DEBUTS_TEST)          # le FUTUR : jamais vu pendant la calibration
    cas = [("calme", 0.0)] + [(t, i) for t in TYPES_INJECTES if t != "forme" for i in INTENSITES] + [("forme", 0.0)]
    lignes = []
    for numero, (typ, inten) in enumerate(cas):
        for k, (ident, w) in enumerate(fen):
            s = w if typ == "calme" else injecter(w, typ, inten, graine=1000 * numero + k)
            x = residus(s)
            for nom, (f, _) in METHODES.items():
                al = garder_zone(f(x, reglages[nom]))
                lig = dict(methode=nom, type=typ, intensite=inten, fenetre=ident)
                if typ == "calme":
                    lig.update(episodes=episodes(al), heures=len(s) - ZONE_JUGEMENT, alerte_avant=int(any(a < T0 for a in al)))
                else:
                    r = evaluer(al, T0)
                    propre = r["detectee"] and r["fausses_alertes"] == 0
                    lig.update(detectee=propre, delai=r["delai"] if propre else None,
                            fausse_alerte=r["fausses_alertes"] > 0)
                lignes.append(lig)
        print(f"cas {numero + 1}/{len(cas)} : {typ} {inten}  ({time.time() - t_debut:.0f} s)", flush=True)
    pd.DataFrame(lignes).to_csv("resultats_semaine5_detection.csv", index=False)
    print("Terminé : resultats_semaine5_detection.csv", len(lignes), "lignes")


if __name__ == "__main__":
    main()