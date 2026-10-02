import numpy as np
from src.generateur import generer_serie, evaluer
from src.generateur import generer_serie

def test_longueur():
    s, _ = generer_serie(n=1000)
    assert len(s) == 1000

def test_reproductible():
    a, _ = generer_serie(seed=3, type_derive="saut_moyenne")
    b, _ = generer_serie(seed=3, type_derive="saut_moyenne")
    assert np.allclose(a, b)

def test_saut_moyenne_monte():
    s, t0 = generer_serie(seed=0, type_derive="saut_moyenne", intensite=3)
    assert s[t0:].mean() > s[:t0].mean() + 5

def test_evaluer_cas_simple():
    r = evaluer([1200, 1720, 1800], t0=1680, tolerance=300)
    assert r == {"detectee": True, "delai": 40, "fausses_alertes": 1}

def test_evaluer_rien_detecte():
    assert evaluer([], t0=1680)["detectee"] is False