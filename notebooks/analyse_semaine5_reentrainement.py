"""Semaine 5 : lire les résultats du réentraînement + figure.
Usage :  python notebooks/analyse_semaine5_reentrainement.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = pd.read_csv("resultats_semaine5_reentrainement.csv")
ORDRE = ["jamais", "tous les 56 j", "tous les 28 j", "tous les 14 j", "tous les 7 j",
        "sur alerte (h=20)", "sur alerte (h=50)", "sur alerte (h=100)", "sur alerte (h=200)", "oracle"]
CONDS = list(dict.fromkeys(d["condition"]))

print("\n=== TABLEAU 1 : erreur moyenne après t0 (en multiples de l'erreur normale) / nombre de réentraînements ===")
t = d.groupby(["condition", "strategie"]).agg(erreur=("mae", "mean"), reentr=("reentrainements", "mean")).reset_index()
aff = t.assign(v=t["erreur"].round(2).astype(str) + "  (" + t["reentr"].round(1).astype(str) + " r.)")
print(aff.pivot(index="strategie", columns="condition", values="v").loc[ORDRE][CONDS].to_string())


def bootstrap(a, b, n=5000, graine=0):
    """Différence moyenne a - b et fourchette à 95 %, en rééchantillonnant les FENÊTRES."""
    rng = np.random.default_rng(graine)
    diff = a - b
    m = [rng.choice(diff, len(diff)).mean() for _ in range(n)]
    return diff.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5)


print("\n=== TABLEAU 2 : 'sur alerte' contre une date fixe (même fenêtres). Différence d'erreur : négatif = l'alerte gagne ===")
paires = [("sur alerte (h=50)", "tous les 28 j"), ("sur alerte (h=20)", "tous les 14 j"), ("sur alerte (h=50)", "tous les 14 j")]
for a, b in paires:
    print(f"\n--- {a}   contre   {b} ---")
    for c in CONDS:
        pa = d[(d.condition == c) & (d.strategie == a)].set_index("fenetre")
        pb = d[(d.condition == c) & (d.strategie == b)].set_index("fenetre")
        m, lo, hi = bootstrap(pa["mae"].values, pb["mae"].loc[pa.index].values)
        dr = (pa["reentrainements"] - pb["reentrainements"].loc[pa.index]).mean()
        verdict = "alerte gagne" if hi < 0 else ("date fixe gagne" if lo > 0 else "pas de différence nette")
        print(f"  {c:12s} écart d'erreur {m:+.2f} [{lo:+.2f} ; {hi:+.2f}]   réentraînements {dr:+.1f}   -> {verdict}")

os.makedirs("figures", exist_ok=True)
fig, axes = plt.subplots(1, len(CONDS), figsize=(4 * len(CONDS), 3.8), sharey=False)
style = {"jamais": ("#898781", "s"), "date fixe": ("#2a78d6", "o"), "alerte": ("#eb6834", "^"), "oracle": ("#1baf7a", "D")}
for ax, c in zip(axes, CONDS):
    for famille, (col, mk) in style.items():
        noms = [s for s in ORDRE if (s == famille or (famille == "date fixe" and s.startswith("tous")) or
                                    (famille == "alerte" and s.startswith("sur alerte")))]
        sub = t[(t.condition == c) & (t.strategie.isin(noms))].sort_values("reentr")
        ax.plot(sub["reentr"], sub["erreur"], color=col, marker=mk, label=famille, lw=1.8)
    ax.set_title(c, fontsize=11)
    ax.set_xlabel("réentraînements (nombre)")
    ax.grid(alpha=.25)
axes[0].set_ylabel("erreur après t0 (plus bas = mieux)")
axes[0].legend(frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("figures/reentrainement.png", dpi=140)
print("\nFigure : figures/reentrainement.png")