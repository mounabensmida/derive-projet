import sys, os, time, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
from src.generateur import generer_serie, TYPES_DERIVE, evaluer
from src.residus import residus
from src.calibration import calibrer
from src.detecteurs_deep import calculer_scores, alertes_depuis_scores, SansReseau

try:
    from src.modeles_torch import AutoEncodeur, PredicteurLSTM
    NOM_PRED = "LSTM"
except ImportError:
    print("PyTorch absent : modèles de secours scikit-learn.")
    from src.modeles_sklearn import AutoEncodeur, PredicteurMLP as PredicteurLSTM
    NOM_PRED = "MLP (secours)"

MARGES = [1.0, 1.2, 1.5, 2.0, 3.0]
MODELES = {
    "Autoencodeur": AutoEncodeur,
    NOM_PRED: PredicteurLSTM,
    "Sans réseau (contrôle)": SansReseau,
}


def fabrique_detecteur(nom, fabrique):
    return lambda x, marge: alertes_depuis_scores(calculer_scores(x, nom, fabrique), marge)


if __name__ == "__main__":
    debut = time.time()
    choix, lignes = {}, []
    for nom, fabrique in MODELES.items():
        print("Calibration :", nom)
        det = fabrique_detecteur(nom, fabrique)
        choix[nom] = calibrer(det, MARGES)
        for typ in TYPES_DERIVE:
            for seed in range(10):
                s, t0 = generer_serie(seed=seed, type_derive=typ, intensite=2.0)
                r = evaluer(det(residus(s), choix[nom]), t0)
                r.update(methode=nom, type=typ)
                lignes.append(r)
    print("\nMarges choisies :", choix)
    json.dump(choix, open("marges_semaine3.json", "w"))

    nouveau = pd.DataFrame(lignes)
    nouveau.to_csv("resultats_semaine3.csv", index=False)
    ancien = pd.read_csv("resultats_semaine2.csv")
    ancien = ancien[ancien["methode"].isin(["CUSUM résidus", "KS résidus"])]
    df = pd.concat([ancien, nouveau])
    tab = df.groupby(["type", "methode"]).agg(
        detection=("detectee", "mean"), delai=("delai", "mean")).round(2)
    print(tab.unstack("methode")["detection"])
    print()
    print(tab.unstack("methode")["delai"])
    print(f"\nDurée : {time.time() - debut:.0f} s")



# C:\Users\Ce pc\Desktop\projet 3 eme\derive-projet>python -m notebooks.bench_semaine3
# Traceback (most recent call last):
#   File "<frozen runpy>", line 198, in _run_module_as_main
#   File "<frozen runpy>", line 88, in _run_code
#   File "C:\Users\Ce pc\Desktop\projet 3 eme\derive-projet\notebooks\bench_semaine3.py", line 8, in <module>
#     from src.evaluation import evaluer
# ModuleNotFoundError: No module named 'src.evaluation'

# C:\Users\Ce pc\Desktop\projet 3 eme\derive-projet>python -m notebooks.bench_semaine3
# Calibration : Autoencodeur
#   réglage 1.0 : 75% de séries calmes avec fausse alerte
#   réglage 1.2 : 60% de séries calmes avec fausse alerte
#   réglage 1.5 : 35% de séries calmes avec fausse alerte
#   réglage 2.0 : 5% de séries calmes avec fausse alerte
# Calibration : LSTM
#   réglage 1.0 : 90% de séries calmes avec fausse alerte
#   réglage 1.2 : 25% de séries calmes avec fausse alerte
#   réglage 1.5 : 5% de séries calmes avec fausse alerte
# Calibration : Sans réseau (contrôle)
#   réglage 1.0 : 85% de séries calmes avec fausse alerte
#   réglage 1.2 : 55% de séries calmes avec fausse alerte
#   réglage 1.5 : 20% de séries calmes avec fausse alerte
#   réglage 2.0 : 10% de séries calmes avec fausse alerte

# Marges choisies : {'Autoencodeur': 2.0, 'LSTM': 1.5, 'Sans réseau (contrôle)': 2.0}
# methode       Autoencodeur  CUSUM résidus  KS résidus  LSTM  Sans réseau (contrôle)
# type
# forme                  0.8            0.0         0.0   0.0                     0.4
# graduelle              1.0            1.0         1.0   0.2                     0.9
# saisonnalite           1.0            1.0         1.0   1.0                     1.0
# saut_moyenne           1.0            1.0         1.0   0.4                     1.0
# variance               1.0            0.8         0.9   1.0                     1.0

# methode       Autoencodeur  CUSUM résidus  KS résidus   LSTM  Sans réseau (contrôle)
# type
# forme               146.88            NaN         NaN    NaN                  135.75
# graduelle           223.70         133.10      139.80  259.0                  187.22
# saisonnalite         11.00          10.20      102.10   10.5                    4.80
# saut_moyenne         58.40          31.50       54.90   93.5                   43.90
# variance             16.30          66.38      168.33   36.6                   12.10

# Durée : 111 s