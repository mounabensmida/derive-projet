import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("resultats_semaine2.csv")
tab = df.groupby(["type", "methode"])["detectee"].mean().unstack("methode")

fig, ax = plt.subplots(figsize=(8, 4))
im = ax.imshow(tab.values, cmap="Greens", vmin=0, vmax=1)
ax.set_xticks(range(len(tab.columns)), tab.columns, rotation=30, ha="right")
ax.set_yticks(range(len(tab.index)), tab.index)
for i in range(tab.shape[0]):
    for j in range(tab.shape[1]):
        ax.text(j, i, f"{tab.values[i, j]:.0%}", ha="center", va="center")
ax.set_title("Taux de détection (seuils calibrés, intensité 2)")
plt.colorbar(im)
plt.tight_layout()
plt.savefig("figures/benchmark_semaine2.png", dpi=150)
plt.show()