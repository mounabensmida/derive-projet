import numpy as np
from src.donnees_reelles import charger, toutes_les_fenetres, fenetres_prevision, LONGUEUR, DEBUTS_TEST, DEBUTS_CALIBRATION
from src.injection import injecter, TYPES_INJECTES, T0
import src.reentrainement as R


def test_donnees_reelles_chargees():
    x = charger("ETTh1", "HUFL")
    assert len(x) == 17420 and not np.isnan(x).any()
    assert all(len(w) == LONGUEUR for _, w in toutes_les_fenetres("ETTh1"))


def test_passe_et_futur_ne_se_chevauchent_pas():
    assert max(DEBUTS_CALIBRATION) + LONGUEUR <= min(DEBUTS_TEST)


def test_injection_ne_touche_pas_avant_t0():
    w = charger("ETTh1", "HUFL")[:LONGUEUR]
    for typ in TYPES_INJECTES:
        s = injecter(w, typ, 4.0, graine=1)
        assert np.allclose(s[:T0], w[:T0]), typ
        assert not np.allclose(s[T0:], w[T0:]), typ


def test_forme_garde_les_memes_valeurs_residuelles():
    from src.residus import residus
    w = charger("ETTh1", "HUFL")[:LONGUEUR]
    s = injecter(w, "forme", 0.0, graine=2)
    assert np.allclose(np.sort(residus(s)[T0:]), np.sort(residus(w)[T0:]))   # mêmes valeurs, autre ordre


def test_jamais_ne_reentraine_pas_et_periodique_oui():
    X, y = fenetres_prevision("ETTh1", DEBUTS_TEST)[0]
    _, r0 = R.simuler(X, y, "jamais")
    _, r1 = R.simuler(X, y, "tous les 28 j")
    assert r0 == [] and len(r1) == 3


def test_reentrainer_aide_sur_un_saut():
    X, y = fenetres_prevision("ETTh1", DEBUTS_TEST)[0]
    yy = R.injecter(X, y, "saut", 3.0, R.sigma_reference(X, y))
    e0, _ = R.simuler(X, yy, "jamais")
    e1, _ = R.simuler(X, yy, "tous les 7 j")
    assert np.nanmean(e1[R.T0:]) < np.nanmean(e0[R.T0:])