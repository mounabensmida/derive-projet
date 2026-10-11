"""La liste des 6 méthodes comparées. Toutes ont la même forme :
f(residus, reglage) -> liste des instants d'alerte."""
from src.detecteurs_stat import page_hinkley, cusum, ks_glissant, mw_glissant
from src.detecteur_reseau import alertes_reseau

GRILLE_P = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]    # du plus nerveux au plus prudent
GRILLE_H = [10, 15, 20, 25, 30, 35, 40, 50]
GRILLE_MARGE = [1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0]

METHODES = {
    "CUSUM":                  (lambda x, r: cusum(x, h=r), GRILLE_H),
    "Page-Hinkley":           (lambda x, r: page_hinkley(x, seuil=r), GRILLE_H),
    "KS":                     (lambda x, r: ks_glissant(x, seuil=r), GRILLE_P),
    "Mann-Whitney":           (lambda x, r: mw_glissant(x, seuil=r), GRILLE_P),
    "Autoencodeur":           (lambda x, r: alertes_reseau(x, r, True), GRILLE_MARGE),
    "Sans réseau (contrôle)": (lambda x, r: alertes_reseau(x, r, False), GRILLE_MARGE),
}