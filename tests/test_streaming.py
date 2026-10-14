"""Le streaming doit donner EXACTEMENT les mêmes alertes que la version par lots (benchmarks)."""
import numpy as np
from src.generateur import generer_serie
from src.residus import residus
from src.detecteurs_stat import cusum
from src.detecteur_reseau import alertes_reseau
from src.evaluation import garder_zone
from src.streaming import rejouer


def _alertes(lignes, nom):
    return [r["t"] for r in lignes if r[f"alerte_{nom}"]]


def test_streaming_egal_au_lot_sur_une_serie_synthetique():
    s, _ = generer_serie(seed=7, type_derive="saut_moyenne", intensite=2.0)
    lignes = list(rejouer(s, cusum_h=20.0, marge_reseau=1.5, marge_controle=1.5))
    x = residus(s)
    assert _alertes(lignes, "cusum") == garder_zone(cusum(x, h=20.0))
    assert _alertes(lignes, "reseau") == alertes_reseau(x, 1.5, True)
    assert _alertes(lignes, "controle") == alertes_reseau(x, 1.5, False)


def test_le_moteur_ne_voit_pas_le_futur():
    """Si on change le FUTUR, ce que le moteur a dit sur le PASSÉ ne change pas."""
    s, _ = generer_serie(seed=3, type_derive="saut_moyenne", intensite=2.0)
    s2 = s.copy()
    s2[2000:] += 100.0
    a = list(rejouer(s))
    b = list(rejouer(s2))
    for r1, r2 in zip(a[:2000], b[:2000]):
        assert (r1["alerte_cusum"], r1["alerte_reseau"]) == (r2["alerte_cusum"], r2["alerte_reseau"])
        assert np.isclose(r1["score_cusum"], r2["score_cusum"], equal_nan=True)


def test_serie_calme_peu_d_alertes():
    s, _ = generer_serie(seed=11)
    lignes = list(rejouer(s))
    assert len(_alertes(lignes, "cusum")) < 100