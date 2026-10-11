import numpy as np
import pytest
from src.detecteurs_deep import (fabriquer_fenetres, lisser, calculer_scores,
                                alertes_depuis_scores, SansReseau, FENETRE)


def bruit(seed=0, n=3000):
    return np.random.default_rng(seed).normal(0, 1, n)


def test_fenetres_formes():
    z = np.arange(100, dtype=float)
    instants, X, y = fabriquer_fenetres(z, 30, 50)
    assert X.shape == (20, FENETRE)
    assert list(X[0]) == list(range(6, 30))     # les 24 valeurs AVANT t = 30
    assert y[0] == 30                            # la valeur à t = 30


def test_lisser_constante():
    sortie = lisser(np.full(100, 2.0), k=10)
    assert np.isnan(sortie[:9]).all()
    assert np.allclose(sortie[9:], 2.0)


def test_controle_calme_sans_alerte():
    sc = calculer_scores(bruit(), "test_calme", SansReseau)
    assert len(alertes_depuis_scores(sc, marge=2.0)) == 0


def test_controle_voit_une_hausse_de_variance():
    x = bruit()
    x[2000:] *= 3
    sc = calculer_scores(x, "test_variance", SansReseau)
    alertes = alertes_depuis_scores(sc, marge=2.0)
    assert len(alertes) > 0
    assert 2000 <= alertes[0] <= 2100


def test_autoencodeur_pytorch():
    pytest.importorskip("torch")
    from src.modeles_torch import AutoEncodeur
    X = np.random.default_rng(0).normal(0, 1, (200, FENETRE))
    modele = AutoEncodeur(epoques=50)
    modele.apprendre(X)
    erreurs = modele.erreurs(X)
    assert erreurs.shape == (200,)
    assert erreurs.mean() < 1.0                  # mieux qu'une réponse "au hasard"