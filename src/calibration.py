"""Choisir le seuil de chaque détecteur pour qu'ils aient le MÊME niveau de fausses alertes."""
from src.generateur import generer_serie
from src.residus import residus


def taux_fausse_alerte(detecteur, seuil, utiliser_residus=True, n_series=20, t0=1680, seed0=100):
    """Part des séries CALMES (sans dérive) où le détecteur alerte au moins une fois avant t0."""
    nb = 0
    for i in range(n_series):
        s, _ = generer_serie(seed=seed0 + i)
        s = s[:t0]
        x = residus(s) if utiliser_residus else s
        if len(detecteur(x, seuil)) > 0:
            nb += 1
    return nb / n_series


def calibrer(detecteur, grille, utiliser_residus=True, cible=0.10, **kw):
    """grille = seuils du PLUS sensible au PLUS prudent. Renvoie le 1er seuil qui respecte la cible."""
    for seuil in grille:
        taux = taux_fausse_alerte(detecteur, seuil, utiliser_residus, **kw)
        print(f"   seuil {seuil}: {taux:.0%} de séries avec fausse alerte")
        if taux <= cible:
            return seuil
    return grille[-1]