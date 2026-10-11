"""Détecteur à réseau de neurones (autoencodeur) et son contrôle sans réseau."""
import numpy as np
from sklearn.neural_network import MLPRegressor
from src.residus import standardiser

FEN = 24                    # le réseau regarde 24 heures d'un coup
ENTRAINEMENT = (672, 1008)  # période normale : le réseau apprend ici
VALIDATION = (1008, 1344)   # autre période normale : on fixe le seuil ici
LISSAGE = 24                # on lisse l'erreur sur 24 heures
_MEMOIRE = {}               # mémoire : on n'entraîne qu'une fois par série


def fenetres(z, debut, fin):
    """Pour chaque instant t : les 24 valeurs juste avant t."""
    return np.array([z[t - FEN:t] for t in range(debut, fin)])


def lisser(e, k=LISSAGE):
    """Moyenne glissante causale : chaque point = moyenne des k derniers."""
    c = np.cumsum(np.insert(e, 0, 0.0))
    out = np.full(len(e), np.nan)
    out[k - 1:] = (c[k:] - c[:-k]) / k
    return out


def scores(x, avec_reseau):
    """x = résidus de la série. Un score par heure : grand = surprenant."""
    cle = (avec_reseau, hash(x.tobytes()))
    if cle not in _MEMOIRE:
        if len(_MEMOIRE) > 200:
            _MEMOIRE.clear()
        z = standardiser(x)
        if avec_reseau:
            reseau = MLPRegressor(hidden_layer_sizes=(8,), activation="tanh",
                                max_iter=600, random_state=0)
            X = fenetres(z, ENTRAINEMENT[0] + FEN, ENTRAINEMENT[1])
            reseau.fit(X, X)                                  # il apprend à recopier le normal
            Xtout = fenetres(z, FEN, len(z))
            erreur = ((reseau.predict(Xtout) - Xtout) ** 2).mean(axis=1)
        else:
            erreur = z[FEN:] ** 2                             # contrôle : valeur au carré
        sc = lisser(np.concatenate([np.zeros(FEN), erreur]))
        sc[:FEN + LISSAGE] = np.nan
        _MEMOIRE[cle] = sc
    return _MEMOIRE[cle]


def alertes_reseau(x, marge, avec_reseau=True):
    """Seuil = marge x le pire score vu pendant la période de validation (normale)."""
    sc = scores(x, avec_reseau)
    pire_normal = np.nanmax(sc[VALIDATION[0] + FEN + LISSAGE:VALIDATION[1]])
    seuil = marge * pire_normal
    return [t for t in range(VALIDATION[1], len(sc)) if sc[t] > seuil]