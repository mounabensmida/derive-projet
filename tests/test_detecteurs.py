import numpy as np
from src.detecteurs_stat import page_hinkley, cusum, ks_glissant, mw_glissant
from src.residus import residus

DETECTEURS = [page_hinkley, cusum, ks_glissant, mw_glissant]


def serie_calme(seed=0, n=3000):
    return np.random.default_rng(seed).normal(0, 1, n)


def serie_avec_saut(seed=0, n=3000, t0=2000, saut=3.0):
    x = np.random.default_rng(seed).normal(0, 1, n)
    x[t0:] += saut
    return x


def test_aucune_alerte_sur_serie_calme():
    for det in DETECTEURS:
        assert len(det(serie_calme())) == 0, det.__name__


def test_alerte_apres_un_gros_saut():
    for det in DETECTEURS:
        alertes = det(serie_avec_saut())
        assert len(alertes) > 0, det.__name__
        assert alertes[0] >= 2000, det.__name__       # pas d'alerte AVANT le saut
        assert alertes[0] <= 2100, det.__name__       # détection rapide


def test_pas_d_alerte_pendant_la_reference():
    # tout changement avant l'instant 1008 ne doit rien déclencher
    x = serie_calme()
    x[800:900] += 10
    for det in [page_hinkley, cusum]:
        assert all(t >= 1008 for t in det(x))


def test_residus_enleve_le_cycle():
    t = np.arange(3360)
    cycle = 20 * np.sin(2 * np.pi * t / 24) + 10 * np.sin(2 * np.pi * t / 168)
    assert np.abs(residus(cycle)).max() < 1e-9