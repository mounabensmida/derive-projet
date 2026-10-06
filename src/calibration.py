"""Calibration : régler chaque détecteur au même niveau de fausses alertes."""
from src.generateur import generer_serie
from src.residus import residus

CIBLE = 0.10          # au plus 10 % des séries calmes ont une fausse alerte
N_CALMES = 20         # nombre de séries calmes (sans dérive)
GRAINE_DEBUT = 100    # graines différentes de celles du banc d'essai (0 à 9)


def taux_fausses_alertes(detecteur, reglage, utiliser_residus=True, n_calmes=N_CALMES):
    """Proportion de séries calmes où le détecteur donne au moins une alerte."""
    nb = 0
    for seed in range(GRAINE_DEBUT, GRAINE_DEBUT + n_calmes):
        s, _ = generer_serie(seed=seed)   # pas de dérive : toute alerte est fausse
        x = residus(s) if utiliser_residus else s
        if len(detecteur(x, reglage)) > 0:
            nb += 1
    return nb / n_calmes


def calibrer(detecteur, grille, utiliser_residus=True, cible=CIBLE, n_calmes=N_CALMES):
    """Retourne le réglage le plus sensible de la grille qui respecte la cible.
    La grille va du plus sensible au plus prudent."""
    for reglage in grille:
        taux = taux_fausses_alertes(detecteur, reglage, utiliser_residus, n_calmes)
        print(f"  réglage {reglage} : {taux:.0%} de séries calmes avec fausse alerte")
        if taux <= cible:
            return reglage
    return grille[-1]   # aucun ne respecte la cible : on garde le plus prudent
