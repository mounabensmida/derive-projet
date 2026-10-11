# import sys, os
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import numpy as np
# from src.detecteurs_deep import calculer_scores, alertes_depuis_scores, SansReseau

# x = np.random.default_rng(0).normal(0, 1, 3000)
# x[2000:] *= 3                                       # l'agitation triple à t = 2000
# scores = calculer_scores(x, "essai", SansReseau)
# alertes = alertes_depuis_scores(scores, marge=2.0)
# print(alertes[:3])                                  # première alerte juste après 2000


import sys, os, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from src.generateur import generer_serie
from src.residus import residus
from src.detecteurs_deep import calculer_scores, alertes_depuis_scores, VALIDATION, FENETRE, LISSAGE, SansReseau
from notebooks.bench_semaine3 import MODELES

marges = json.load(open("marges_semaine3.json"))
types = ["saut_moyenne", "variance", "forme"]
fig, axes = plt.subplots(len(types), 1, figsize=(11, 9), sharex=True)
for ax, typ in zip(axes, types):
    s, t0 = generer_serie(seed=3, type_derive=typ, intensite=2.0)
    x = residus(s)
    for nom, fabrique in MODELES.items():
        sc = calculer_scores(x, nom + "_fig", fabrique)
        pire = np.nanmax(sc[VALIDATION[0] + FENETRE + LISSAGE:VALIDATION[1]])
        ax.plot(sc / (marges[nom] * pire), lw=0.9, label=nom)
    ax.axhline(1, color="black", ls=":", lw=1)
    ax.axvline(t0, color="red", ls="--", lw=1.5)
    ax.set_ylim(0, 5)
    ax.set_ylabel(typ)
axes[0].legend(loc="upper left", fontsize=8)
axes[0].set_title("Score / seuil : au-dessus de la ligne pointillée = alerte ; ligne rouge = vraie rupture")
plt.tight_layout()
plt.savefig("figures/scores_semaine3.png", dpi=150)
plt.show()