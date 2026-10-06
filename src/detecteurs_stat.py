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


def page_hinkley(serie, delta=0.5, seuil=25.0, debut=DEBUT):
    """Alerte quand la moyenne monte OU baisse durablement.
    PH = on regarde de combien le cumul a remonté depuis son point le plus bas."""
    z = standardiser(serie, debut)
    alertes = []
    s_h = m_h = s_b = max_b = 0.0     # sommes cumulées (hausse / baisse)
    moy, n = 0.0, 0
    for t in range(debut + LONG_REF, len(z)):
        x = z[t]
        n += 1
        moy += (x - moy) / n            # moyenne courante, mise à jour point par point
        s_h += x - moy - delta
        m_h = min(m_h, s_h)
        s_b += x - moy + delta
        max_b = max(max_b, s_b)
        if (s_h - m_h) > seuil or (max_b - s_b) > seuil:
            alertes.append(t)
    return alertes


def _fenetre_glissante(serie, test, w, seuil, debut):
    reference = serie[debut:debut + w]
    alertes = []
    for t in range(debut + 2 * w, len(serie)): #2 * w  pour que la fenêtre courante ne chevauche pas la référence.
        courante = serie[t - w:t]
        if test(reference, courante) < seuil:
            alertes.append(t)
    return alertes


def ks_glissant(serie, seuil=1e-5, w=168, debut=DEBUT):
    """KS : compare la FORME COMPLÈTE de deux fenêtres."""
    return _fenetre_glissante(serie, lambda a, b: ks_2samp(a, b).pvalue, w, seuil, debut)


def mw_glissant(serie, seuil=1e-5, w=168, debut=DEBUT):
    """Mann-Whitney : une fenêtre a-t-elle tendance à avoir des valeurs plus grandes ?"""
    return _fenetre_glissante(serie, lambda a, b: mannwhitneyu(a, b).pvalue, w, seuil, debut)
