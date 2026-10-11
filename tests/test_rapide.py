import numpy as np
from scipy.stats import ks_2samp, mannwhitneyu
from src.generateur import generer_serie
from src.residus import residus
from src.detecteurs_stat import _pvaleurs


def test_p_values_rapides_egales_a_scipy():
    """La version rapide doit donner les MÊMES p-values que scipy, point par point."""
    s, _ = generer_serie(seed=5, type_derive="variance", intensite=2.0)
    x = residus(s)
    w, debut = 168, 672
    reference = x[debut:debut + w]
    for nom, test in [("ks", ks_2samp), ("mw", mannwhitneyu)]:
        rapide = _pvaleurs(x, nom, w, debut)
        for t in range(debut + 2 * w, len(x), 50):             # on vérifie 1 instant sur 50
            lent = test(reference, x[t - w:t]).pvalue
            assert np.isclose(rapide[t], lent, rtol=1e-6, atol=1e-300), (nom, t, rapide[t], lent)