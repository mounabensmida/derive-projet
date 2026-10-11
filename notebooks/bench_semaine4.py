"""Benchmark de la semaine 4 : 6 méthodes x 5 dérives x 3 intensités x 3 niveaux de bruit.
Usage :  python notebooks/bench_semaine4.py [nb_series_par_case] [nb_coeurs]
Exemple :  python notebooks/bench_semaine4.py 30 2      (30 séries par case, 2 cœurs)
        python notebooks/bench_semaine4.py 5         (essai rapide)"""
import sys, os, time, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from itertools import product
import pandas as pd
from src.generateur import generer_serie, TYPES_DERIVE
from src.evaluation import evaluer, garder_zone, episodes, ZONE_JUGEMENT
from src.residus import residus
from src.calibration import calibrer
from src.methodes import METHODES

INTENSITES = [1.0, 2.0, 3.0]
BRUITS = [3.0, 5.0, 8.0]
FICHIER_REGLAGES = "reglages_semaine4.json"


def calibrer_tout(n_series=50):
    """Règle chaque méthode sur 50 séries CALMES (graines 100 à 149), jugées à partir de t = 1344."""
    reglages = {}
    for nom, (f, grille) in METHODES.items():
        print("Calibration :", nom, flush=True)
        detecteur = lambda x, r, f=f: garder_zone(f(x, r))
        reglages[nom] = calibrer(detecteur, grille, utiliser_residus=True, n_series=n_series)
    json.dump(reglages, open(FICHIER_REGLAGES, "w"), indent=1)
    return reglages


def liste_cases(n_series):
    """Chaque case (dérive, intensité, bruit) a ses propres séries : graine = 1000 x numéro de case + k."""
    cases = [(typ, i, b) for typ, i, b in product(TYPES_DERIVE, INTENSITES, BRUITS)]
    cases += [("calme", 0.0, b) for b in BRUITS]
    travaux = []
    for numero, (typ, intensite, bruit) in enumerate(cases):
        for k in range(n_series):
            travaux.append((typ, intensite, bruit, 1000 * numero + k))
    return travaux


def travailler(args):
    """Génère UNE série et fait passer les 6 méthodes dessus."""
    typ, intensite, bruit, graine, reglages = args
    s, t0 = generer_serie(seed=graine, type_derive=None if typ == "calme" else typ,
                        intensite=intensite, sigma=bruit)
    x = residus(s)
    lignes = []
    for nom, (f, _) in METHODES.items():
        alertes = garder_zone(f(x, reglages[nom]))
        ligne = dict(methode=nom, type=typ, intensite=intensite, bruit=bruit, graine=graine)
        if typ == "calme":
            ligne.update(episodes=episodes(alertes), heures=len(s) - ZONE_JUGEMENT)
        else:
            r = evaluer(alertes, t0)
            propre = r["detectee"] and r["fausses_alertes"] == 0
            ligne.update(detectee=propre, delai=r["delai"] if propre else None,
                        fausse_alerte=r["fausses_alertes"] > 0)
        lignes.append(ligne)
    return lignes


if __name__ == "__main__":
    n_series = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    coeurs = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    debut = time.time()

    if os.path.exists(FICHIER_REGLAGES):
        reglages = json.load(open(FICHIER_REGLAGES))
        print("Réglages relus depuis", FICHIER_REGLAGES, "(supprimez ce fichier pour recalibrer)")
    else:
        reglages = calibrer_tout()
    print("Réglages :", reglages, flush=True)

    travaux = [t + (reglages,) for t in liste_cases(n_series)]
    print(f"{len(travaux)} séries à traiter ({n_series} par case), {coeurs} cœur(s)", flush=True)
    lignes = []
    if coeurs > 1:
        from multiprocessing import Pool
        with Pool(coeurs) as pool:
            for i, res in enumerate(pool.imap(travailler, travaux, chunksize=4), 1):
                lignes += res
                if i % 100 == 0:
                    print(f"  {i}/{len(travaux)}  ({time.time() - debut:.0f} s)", flush=True)
    else:
        for i, t in enumerate(travaux, 1):
            lignes += travailler(t)
            if i % 100 == 0:
                print(f"  {i}/{len(travaux)}  ({time.time() - debut:.0f} s)", flush=True)

    pd.DataFrame(lignes).to_csv("resultats_semaine4.csv", index=False)
    print(f"Terminé : resultats_semaine4.csv ({len(lignes)} lignes) en {time.time() - debut:.0f} s")