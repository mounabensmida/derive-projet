"""Petits outils statistiques : barre d'erreur et comparaison de deux méthodes."""
import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

CLES = ["type", "intensite", "bruit", "graine"]    # identifie UNE série (même série pour toutes les méthodes)


def intervalle_wilson(succes, total, z=1.96):
    """Fourchette à 95 % pour un taux (ex. 18 détections sur 30 -> entre 42 % et 75 %)."""
    if total == 0:
        return np.nan, np.nan
    p = succes / total
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    marge = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return centre - marge, centre + marge


def comparer(df, a, b, type_derive):
    """Compare les méthodes a et b, SÉRIE PAR SÉRIE, sur un type de dérive.
    Renvoie un dictionnaire avec les taux, le test de détection et le test des délais."""
    d = df[df["type"] == type_derive]
    A = d[d["methode"] == a].set_index(CLES)
    B = d[d["methode"] == b].set_index(CLES)
    A, B = A.align(B, join="inner")
    da, db = A["detectee"].astype(bool), B["detectee"].astype(bool)
    n_a_seul = int((da & ~db).sum())                 # séries vues par a seulement
    n_b_seul = int((~da & db).sum())                 # séries vues par b seulement
    p_detection = (binomtest(n_a_seul, n_a_seul + n_b_seul, 0.5).pvalue
                if n_a_seul + n_b_seul > 0 else 1.0)
    les_deux = da & db
    delais_a, delais_b = A.loc[les_deux, "delai"].astype(float), B.loc[les_deux, "delai"].astype(float)
    if len(delais_a) >= 10 and (delais_a - delais_b).abs().sum() > 0:
        p_delai = wilcoxon(delais_a, delais_b).pvalue
    else:
        p_delai = np.nan
    return dict(taux_a=da.mean(), taux_b=db.mean(), a_seul=n_a_seul, b_seul=n_b_seul,
                p_detection=p_detection, n_paires_delai=int(les_deux.sum()),
                delai_a=delais_a.median() if len(delais_a) else np.nan,
                delai_b=delais_b.median() if len(delais_b) else np.nan, p_delai=p_delai)