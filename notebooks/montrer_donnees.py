"""Jour 1 : regarder les vraies données (et leur dérive naturelle). Usage : python notebooks/montrer_donnees.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.donnees_reelles import charger

x = charger("ETTh1", "HUFL")
print("Nombre d'heures :", len(x), "= environ", len(x) // 24, "jours")
print("Moyenne :", x.mean().round(2), "  écart-type :", x.std().round(2))
mois = [x[i:i + 720].mean() for i in range(0, len(x) - 719, 720)]      # une moyenne par bloc de 30 jours
print("Moyenne par bloc de 30 jours :", np.round(mois, 1))

fig, ax = plt.subplots(2, 1, figsize=(11, 6))
ax[0].plot(x, lw=.4, color="#2a78d6"); ax[0].set_title("Charge HUFL : 2 ans, une valeur par heure")
ax[1].plot(x[:336], color="#2a78d6"); ax[1].set_title("Zoom : 2 semaines (le cycle jour/nuit)")
for a in ax: a.grid(alpha=.25)
plt.tight_layout(); os.makedirs("figures", exist_ok=True); plt.savefig("figures/donnees_reelles.png", dpi=130)
print("Figure : figures/donnees_reelles.png")