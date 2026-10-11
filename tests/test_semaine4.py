import numpy as np
from src.generateur import generer_serie, SIGMA
from src.evaluation import episodes, garder_zone, ZONE_JUGEMENT
from src.detecteur_reseau import alertes_reseau
from src.residus import residus


def test_bruit_plus_fort_donne_plus_agite():
    calme, _ = generer_serie(seed=1, sigma=3)
    agite, _ = generer_serie(seed=1, sigma=8)
    # même hasard, bruit 8 au lieu de 3 : l'écart entre les deux séries vaut 8 - 3 = 5
    assert abs(np.std(agite - calme) - 5.0) < 0.01


def test_sigma_par_defaut_inchange():
    a, _ = generer_serie(seed=5, type_derive="variance")
    b, _ = generer_serie(seed=5, type_derive="variance", sigma=SIGMA)
    assert np.allclose(a, b)


def test_episodes():
    assert episodes([]) == 0
    assert episodes([100, 101, 102]) == 1                 # un seul épisode
    assert episodes([100, 101, 200, 201]) == 2            # deux épisodes
    assert episodes([100, 124, 148]) == 1                 # écart de 24 h : même épisode


def test_garder_zone():
    assert garder_zone([100, 1343, 1344, 2000]) == [1344, 2000]


def test_controle_sans_reseau_voit_la_variance():
    s, t0 = generer_serie(seed=1, type_derive="variance", intensite=2.0)
    alertes = alertes_reseau(residus(s), 1.5, avec_reseau=False)
    assert len(alertes) > 0 and alertes[0] >= t0 - 5