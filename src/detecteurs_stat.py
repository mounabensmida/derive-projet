"""Détecteurs statistiques. Même règle pour tous :
entrée = une série ; sortie = la liste des instants d'alerte."""
from scipy.stats import ks_2samp, mannwhitneyu
from src.residus import DEBUT, LONG_REF, standardiser


def cusum(serie, k=0.5, h=20.0, debut=DEBUT):
    """Alerte quand les écarts à la référence s'accumulent dans le même sens."""
    z = standardiser(serie, debut)
    alertes = []
    s_h = s_b = 0.0
    for t in range(debut + LONG_REF, len(z)): #On ne commence à détecter qu'après la période de référence
        s_h = max(0.0, s_h + z[t] - k)      # seau "hausse"
        s_b = max(0.0, s_b - z[t] - k)      # seau "baisse"
        if s_h > h or s_b > h:
            alertes.append(t)
    return alertes