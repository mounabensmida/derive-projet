import matplotlib.pyplot as plt
from src.generateur import generer_serie, TYPES_DERIVE

fig, axes = plt.subplots(len(TYPES_DERIVE) + 1, 1, figsize=(12, 10), sharex=True)
for ax, typ in zip(axes, [None] + TYPES_DERIVE):
    s, t0 = generer_serie(seed=1, type_derive=typ, intensite=1.0)
    ax.plot(s, lw=0.6)
    if t0:
        ax.axvline(t0, color="red", ls="--")
    ax.set_ylabel(typ or "aucune", rotation=0, ha="right")
plt.tight_layout()
plt.savefig("figures/types_derive.png", dpi=150)
plt.show()