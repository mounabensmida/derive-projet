"""Évaluation : noter un détecteur à partir de ses alertes et de la vraie rupture t0."""
import numpy as np

ZONE_JUGEMENT = 1344   # tous les détecteurs sont jugés à partir de cet instant


def evaluer(alertes, t0, tolerance=300):
    """Note un détecteur sur UNE série. alertes = liste des instants d'alerte."""
    alertes = np.asarray(alertes) #asarray convertit la liste d'alertes en tableau numpy
    avant = alertes[alertes < t0]
    dans_fenetre = alertes[(alertes >= t0) & (alertes <= t0 + tolerance)] # on ne garde que les alertes qui sont dans la fenêtre de tolérance
    detectee = len(dans_fenetre) > 0 #si il y a au moins une alerte dans la fenêtre de tolérance, alors la dérive est détectée
    return {
        "detectee": detectee,
        "delai" : int(dans_fenetre[0] -t0) if detectee else None,
        "fausses_alertes": int(len(avant)),
    }
    """alertes = [1200, 1720, 1800], t0 = 1680.
    1200 < 1680 → fausse alerte
    1720 est dans [1680, 1980] → détectée, délai = 1720 − 1680 = 40
    1800 : alerte de plus, ignorée
    Résultat attendu : {"detectee": True, "delai": 40, "fausses_alertes": 1}"""

def garder_zone(alertes, debut=ZONE_JUGEMENT):
    """On ignore les alertes d'avant l'instant 1344 : même terrain de jeu pour tous."""
    return [t for t in alertes if t >= debut]


def episodes(alertes, ecart=24):
    """Compte les épisodes d'alerte : des alertes espacées de moins de 24 h = 1 seul épisode."""
    n, dernier = 0, None
    for t in alertes:
        if dernier is None or t - dernier > ecart:
            n += 1
        dernier = t
    return n