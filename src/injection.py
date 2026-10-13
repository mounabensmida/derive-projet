"""Injecter une dérive dans une VRAIE série. Tailles exprimées en 'écarts-types' de la série réelle."""
import numpy as np
from src.residus import residus

T0 = 1680
TYPES_INJECTES = ["saut_moyenne", "graduelle", "variance", "saisonnalite", "forme"]


def echelle(serie):
    """Écart-type 'normal' de la série : celui des résidus entre les heures 672 et 1008."""
    return residus(serie)[672:1008].std()


def injecter(serie, type_derive, intensite, graine, t0=T0, duree=200):
    """Renvoie une copie de la série avec une dérive à partir de t0 (rien avant t0)."""
    rng = np.random.default_rng(graine)
    s = serie.copy()
    sig = echelle(serie)
    n = len(s)
    t = np.arange(n)
    apres = t >= t0
    if type_derive == "saut_moyenne":          # la moyenne saute d'un coup
        s[apres] += intensite * sig
    elif type_derive == "graduelle":           # la moyenne monte doucement pendant 200 h, puis reste en haut
        s += intensite * sig * np.clip((t - t0) / duree, 0, 1)
    elif type_derive == "variance":            # du bruit en plus
        s[apres] += rng.normal(0, intensite * sig / 2, apres.sum())
    elif type_derive == "saisonnalite":        # le cycle de 24 h devient plus fort
        s[apres] += (intensite * sig / 2) * np.sin(2 * np.pi * t[apres] / 24)
    elif type_derive == "forme":               # on mélange les résidus : même valeurs, plus de mémoire
        res = residus(serie)
        profil = serie - res
        s[apres] = profil[apres] + rng.permutation(res[apres])
    else:
        raise ValueError(type_derive)
    return s