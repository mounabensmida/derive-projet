"""Lit resultats_semaine4.csv et produit les tableaux, les tests et les figures."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.statistiques import intervalle_wilson, comparer

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
ORDRE = ["CUSUM", "Page-Hinkley", "KS", "Mann-Whitney", "Autoencodeur", "Sans réseau (contrôle)"]
COULEURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#898781"]
MARQUEURS = ["o", "s", "^", "D", "v", "x"]

df = pd.read_csv("resultats_semaine4.csv")
derive = df[df["type"] != "calme"].copy()
calme = df[df["type"] == "calme"].copy()
derive["detectee"] = derive["detectee"].astype(bool)

# ---------- Tableau 1 : taux de détection (intensité 2), avec fourchette à 95 % ----------
print("\n=== 1. Taux de détection, intensité 2 (fourchette à 95 % entre crochets) ===")
t1 = derive[derive["intensite"] == 2.0]
lignes = {}
for typ in t1["type"].unique():
    ligne = {}
    for m in ORDRE:
        d = t1[(t1["type"] == typ) & (t1["methode"] == m)]["detectee"]
        bas, haut = intervalle_wilson(d.sum(), len(d))
        ligne[m] = f"{d.mean():4.0%} [{bas:.0%}-{haut:.0%}]"
    lignes[typ] = ligne
print(pd.DataFrame(lignes).T[ORDRE].to_string())
print(f"(chaque case = {len(d)} séries : 3 niveaux de bruit x {len(d) // 3} graines)")

# ---------- Tableau 2 : taux de détection selon l'intensité ----------
print("\n=== 2. Taux de détection selon l'intensité (moyenne sur les 3 niveaux de bruit) ===")
t2 = derive.groupby(["type", "intensite", "methode"])["detectee"].mean().unstack("methode")[ORDRE]
print((t2 * 100).round(0).astype(int).to_string())

# ---------- Tableau 3 : délai médian (intensité 2) ----------
print("\n=== 3. Délai médian en heures, intensité 2 (vide = jamais détectée) ===")
t3 = t1.groupby(["type", "methode"])["delai"].median().unstack("methode")[ORDRE].round(0)
print(t3.to_string())

# ---------- Tableau 4 : effet du bruit ----------
print("\n=== 4. Effet du bruit : détection du saut de moyenne, intensité 1 ===")
t4 = derive[(derive["type"] == "saut_moyenne") & (derive["intensite"] == 1.0)]
print((t4.groupby(["bruit", "methode"])["detectee"].mean().unstack("methode")[ORDRE] * 100).round(0).astype(int).to_string())

# ---------- Tableau 5 : fausses alertes sur séries calmes ----------
print("\n=== 5. Fausses alertes sur séries calmes (surveillance de t = 1344 à 3360) ===")
g = calme.groupby("methode")
t5 = pd.DataFrame({
    "séries avec >= 1 fausse alerte": g.apply(lambda d: f"{(d['episodes'] > 0).mean():.0%}"),
    "fausses alertes / 1000 h": g.apply(lambda d: round(d["episodes"].sum() / d["heures"].sum() * 1000, 2)),
    "1 fausse alerte toutes les (h)": g.apply(lambda d: round(d["heures"].sum() / max(d["episodes"].sum(), 1))),
}).loc[ORDRE]
print(t5.to_string())
print("(1 fausse alerte toutes les 2000 h = environ 3 mois)")

# ---------- Tests statistiques ----------
print("\n=== 6. Tests : A et B donnent-ils des résultats vraiment différents ? ===")
print("p-value < 0,01 = différence nette (seuil 0,05 / 5 types, car on fait 5 tests)")
PAIRES = [("Autoencodeur", "Sans réseau (contrôle)"), ("CUSUM", "Page-Hinkley"), ("KS", "Mann-Whitney"),
          ("CUSUM", "Autoencodeur")]


def fmt_p(p):
    if pd.isna(p):
        return "  -  "
    return "<0.001" if p < 0.001 else f"{p:.3f}"


for a, b in PAIRES:
    print(f"\n--- A = {a}   contre   B = {b} ---")
    lignes = []
    for typ in derive["type"].unique():
        r = comparer(derive, a, b, typ)
        lignes.append({
            "dérive": typ,
            "détection A": f"{r['taux_a']:.0%}", "détection B": f"{r['taux_b']:.0%}",
            "vue par A seul": int(r["a_seul"]), "vue par B seul": int(r["b_seul"]),
            "p (détection)": fmt_p(r["p_detection"]),
            "délai A (h)": r["delai_a"], "délai B (h)": r["delai_b"],
            "séries comparées": r["n_paires_delai"], "p (délai)": fmt_p(r["p_delai"])})
    print(pd.DataFrame(lignes).set_index("dérive").to_string())

# ---------- Figures ----------
os.makedirs("figures", exist_ok=True)
types = list(derive["type"].unique())
fig, axes = plt.subplots(1, len(types), figsize=(15, 3.6), sharey=True)
for ax, typ in zip(axes, types):
    for m, c, mk in zip(ORDRE, COULEURS, MARQUEURS):
        d = derive[(derive["type"] == typ) & (derive["methode"] == m)]
        taux = d.groupby("intensite")["detectee"].mean() * 100
        ax.plot(taux.index, taux.values, color=c, marker=mk, lw=1.8, ms=6, label=m,
                ls="--" if "contrôle" in m else "-")
    ax.set_title(typ); ax.set_xticks([1, 2, 3]); ax.set_xlabel("intensité")
    ax.set_ylim(-3, 103); ax.grid(axis="y", color="#e1e0d9", lw=0.8)
axes[0].set_ylabel("% de séries où la dérive est vue")
axes[0].legend(fontsize=7, loc="lower right")
plt.tight_layout(); plt.savefig("figures/detection_vs_intensite.png", dpi=140); plt.close()

fig, ax = plt.subplots(figsize=(8, 3.6))
positions = np.arange(len(ORDRE))
valeurs = [t5.loc[m, "1 fausse alerte toutes les (h)"] for m in ORDRE]
ax.barh(positions, valeurs, color=COULEURS, height=0.55)
ax.set_yticks(positions, ORDRE); ax.invert_yaxis()
for p, v in zip(positions, valeurs):
    ax.text(v, p, f" {v} h", va="center", fontsize=9)
ax.set_xlabel("heures entre deux fausses alertes (plus grand = mieux)")
ax.grid(axis="x", color="#e1e0d9", lw=0.8)
plt.tight_layout(); plt.savefig("figures/fausses_alertes.png", dpi=140); plt.close()

fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=False)
for ax, typ in zip(axes, ["saut_moyenne", "variance", "forme"]):
    d = t1[t1["type"] == typ]
    donnees = [d[(d["methode"] == m) & d["detectee"]]["delai"].astype(float).values for m in ORDRE]
    ax.boxplot([x if len(x) else [np.nan] for x in donnees], showfliers=False)
    ax.set_xticks(range(1, 7), ["CUSUM", "PH", "KS", "MW", "Auto", "Contr."], fontsize=8)
    ax.set_title(typ); ax.grid(axis="y", color="#e1e0d9", lw=0.8)
axes[0].set_ylabel("délai de détection (heures)")
plt.tight_layout(); plt.savefig("figures/delais.png", dpi=140); plt.close()
print("\nFigures : figures/detection_vs_intensite.png, figures/fausses_alertes.png, figures/delais.png")