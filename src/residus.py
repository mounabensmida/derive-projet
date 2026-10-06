"""Retirer le cycle normal d'une série pour ne garder que ce qui est inhabituel."""
import numpy as np

N_PROFIL = 672    # 4 semaines pour apprendre le cycle normal
DEBUT = 672       # la période de référence commence ici (semaine 5)
LONG_REF = 336    # 2 semaines de référence


def residus(serie, periode=168, n_profil=N_PROFIL):
    """Série moins son profil moyen sur une semaine (appris sur les 4 premières semaines)."""
    ref =  serie[:n_profil]
    profil = np.array([ref[k::periode].mean() for k in range(periode)])
    # profil est un tableau numpy de taille 'periode' qui contient la moyenne des valeurs de la série pour chaque position dans le cycle hebdomadaire, calculée à partir des n_profil premières valeurs de la série.
    #role de array est de créer un tableau numpy à partir d'une liste ou d'un autre objet séquentiel. Cela permet de bénéficier des fonctionnalités et des performances de numpy pour les opérations sur les tableaux.
    return serie - profil[np.arange(len(serie)) % periode]

def standardiser(res, debut=DEBUT, long_ref=LONG_REF):
    """Met la série à l'échelle 'normale' : moyenne 0 et écart-type 1 sur la référence."""
    ref = res[debut:debut + long_ref]
    return (res - ref.mean()) / ref.std()