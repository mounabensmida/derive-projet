import pandas as pd
from src.statistiques import intervalle_wilson, comparer


def test_wilson_18_sur_30():
    bas, haut = intervalle_wilson(18, 30)
    assert 0.40 < bas < 0.44 and 0.73 < haut < 0.77      # fourchette connue : environ 42 % - 75 %


def test_wilson_plus_etroit_avec_plus_de_series():
    b1, h1 = intervalle_wilson(7, 10)
    b2, h2 = intervalle_wilson(70, 100)
    assert (h2 - b2) < (h1 - b1)


def donnees_test():
    lignes = []
    for graine in range(40):
        for m, vu in [("A", True), ("B", graine < 10)]:      # A voit tout, B voit seulement 10 séries sur 40
            lignes.append(dict(methode=m, type="x", intensite=1.0, bruit=5.0, graine=graine,
                            detectee=vu, delai=10 if vu else None))
    return pd.DataFrame(lignes)


def test_comparer_voit_la_difference():
    r = comparer(donnees_test(), "A", "B", "x")
    assert r["a_seul"] == 30 and r["b_seul"] == 0
    assert r["p_detection"] < 0.001


def test_comparer_methodes_identiques():
    r = comparer(donnees_test(), "A", "A", "x")
    assert r["a_seul"] == 0 and r["b_seul"] == 0 and r["p_detection"] == 1.0