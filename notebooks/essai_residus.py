import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from src.generateur import generer_serie
from src.residus import residus

s, t0 = generer_serie(seed=1, type_derive="saut_moyenne", intensite=2.0)
r = residus(s)

fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
axes[0].plot(s, lw=0.6); axes[0].set_title("Série brute (les cycles cachent la dérive)")
axes[1].plot(r, lw=0.6, color="green"); axes[1].set_title("Résidus (la dérive devient visible)")
for ax in axes:
    ax.axvline(t0, color="red", ls="--")
plt.tight_layout(); plt.show()