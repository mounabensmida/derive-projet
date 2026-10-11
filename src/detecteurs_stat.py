"""Détecteurs statistiques. Même règle pour tous :
entrée = une série ; sortie = la liste des instants d'alerte."""
from functools import lru_cache
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.stats import ks_2samp, norm
from src.residus import DEBUT, LONG_REF, standardiser

_CACHE_P = {}     # mémoire : les p-values d'une série ne sont calculées qu'UNE fois


def page_hinkley(serie, delta=0.5, seuil=25.0, debut=DEBUT):
    """Alerte quand la moyenne monte OU baisse durablement."""
    z = standardiser(serie, debut)
    alertes = []
    s_h = m_h = s_b = max_b = 0.0     # sommes cumulées (hausse / baisse)
    moy, n = 0.0, 0
    for t in range(debut + LONG_REF, len(z)):
        x = z[t]
        n += 1
        moy += (x - moy) / n            # moyenne courante
        s_h += x - moy - delta
        m_h = min(m_h, s_h)
        s_b += x - moy + delta
        max_b = max(max_b, s_b)
        if (s_h - m_h) > seuil or (max_b - s_b) > seuil:
            alertes.append(t)
    return alertes


def cusum(serie, k=0.5, h=20.0, debut=DEBUT):
    """Alerte quand les écarts à la référence s'accumulent dans le même sens."""
    z = standardiser(serie, debut)
    alertes = []
    s_h = s_b = 0.0
    for t in range(debut + LONG_REF, len(z)):
        s_h = max(0.0, s_h + z[t] - k)
        s_b = max(0.0, s_b - z[t] - k)
        if s_h > h or s_b > h:
            alertes.append(t)
    return alertes


def _fenetres_et_reference(serie, w, debut):
    """Renvoie la référence (w valeurs) et, pour chaque instant t >= debut + 2w,
    la fenêtre courante (les w valeurs avant t), toutes d'un coup dans un tableau."""
    reference = serie[debut:debut + w]
    t_depart = debut + 2 * w
    fenetres = sliding_window_view(serie, w)[t_depart - w:len(serie) - w]
    return reference, fenetres, t_depart


@lru_cache(maxsize=None)          # calculée une seule fois, puis réutilisée
def _table_ks(w):
    """p-value exacte de KS pour chaque écart possible D = k / w (calculée par scipy, une seule fois)."""
    table = np.ones(w + 1)
    for k in range(1, w + 1):
        a = np.arange(w, dtype=float)
        table[k] = ks_2samp(a, a + (k - 0.5)).pvalue      # deux paquets décalés : D = k / w
    return table


def _pvaleurs_ks(serie, w, debut):
    reference, fenetres, t_depart = _fenetres_et_reference(serie, w, debut)
    n = len(fenetres)
    pool = np.concatenate([np.broadcast_to(reference, (n, w)), fenetres], axis=1)
    etiquette = np.concatenate([np.zeros(w), np.ones(w)])[np.argsort(pool, axis=1, kind="stable")]
    # on avance dans l'ordre croissant : +1/w pour une valeur de la référence, -1/w pour la fenêtre
    ecart = np.cumsum((etiquette == 0) / w - (etiquette == 1) / w, axis=1)
    k = np.rint(np.abs(ecart).max(axis=1) * w).astype(int)
    p = np.ones(len(serie))
    p[t_depart:] = _table_ks(w)[k]
    return p


def _pvaleurs_mw(serie, w, debut):
    reference, fenetres, t_depart = _fenetres_et_reference(serie, w, debut)
    n = len(fenetres)
    pool = np.concatenate([np.broadcast_to(reference, (n, w)), fenetres], axis=1)
    rangs = pool.argsort(axis=1).argsort(axis=1) + 1            # rang de chaque valeur
    u = rangs[:, :w].sum(axis=1) - w * (w + 1) / 2              # statistique U de Mann-Whitney
    sigma = np.sqrt(w * w * (2 * w + 1) / 12)
    z = (np.maximum(u, w * w - u) - w * w / 2 - 0.5) / sigma
    p = np.ones(len(serie))
    p[t_depart:] = np.minimum(1.0, 2 * norm.sf(z))
    return p


def _pvaleurs(serie, nom, w, debut):
    """Une p-value par instant. Calculée une seule fois par série (mémoire)."""
    cle = (nom, hash(serie.tobytes()), w, debut)
    if cle not in _CACHE_P:
        if len(_CACHE_P) > 200:
            _CACHE_P.clear()
        calcul = _pvaleurs_ks if nom == "ks" else _pvaleurs_mw
        _CACHE_P[cle] = calcul(serie, w, debut)
    return _CACHE_P[cle]


def ks_glissant(serie, seuil=1e-5, w=168, debut=DEBUT):
    """KS : compare la FORME COMPLÈTE de deux fenêtres."""
    p = _pvaleurs(serie, "ks", w, debut)
    return [int(t) for t in np.where(p < seuil)[0]]


def mw_glissant(serie, seuil=1e-5, w=168, debut=DEBUT):
    """Mann-Whitney : une fenêtre a-t-elle tendance à avoir des valeurs plus grandes ?"""
    p = _pvaleurs(serie, "mw", w, debut)
    return [int(t) for t in np.where(p < seuil)[0]]