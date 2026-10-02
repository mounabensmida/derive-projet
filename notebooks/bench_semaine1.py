import pandas as pd
from src.generateur import generer_serie, TYPES_DERIVE
from src.evaluation import evaluer
from src.detecteurs_base import detecteur_ks

lignes = []
for typ in TYPES_DERIVE:
    for seed in range(10):                      # 10 séries par type
        s, t0 = generer_serie(seed=seed, type_derive=typ, intensite=1.0)
        r = evaluer(detecteur_ks(s), t0)
        r.update(type=typ, seed=seed)
        lignes.append(r)

df = pd.DataFrame(lignes)
print(df.groupby("type").agg(
    taux_detection=("detectee", "mean"),
    delai_moyen=("delai", "mean"),
    fausses_alertes=("fausses_alertes", "mean"),
).round(2))