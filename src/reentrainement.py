"""Quand faut-il réentraîner un modèle de prévision ? On compare des stratégies.

Le modèle prévoit la température de l'huile (y) à partir des charges (X).
On surveille son ERREUR avec CUSUM : si l'erreur dérive, on réentraîne."""
import numpy as np
from sklearn.linear_model import Ridge
from src.detecteurs_stat import cusum

T0 = 1680            # instant où l'on injecte une dérive (si on en injecte)
DEBUT_MODELE = 672   # le modèle est entraîné sur les 4 premières semaines, puis mis en service
FENETRE = 672        # un réentraînement utilise les 4 dernières semaines
ATTENTE = 168        # après une alerte, on attend 1 semaine (pour voir des données du "nouveau monde")
ZONE = 1344          # on n'agit sur une alerte qu'à partir de cet instant (comme en semaine 4)
STRATEGIES = ["jamais", "tous les 28 j", "tous les 14 j", "tous les 7 j", "sur alerte", "oracle"]
PERIODES = {"tous les 28 j": 672, "tous les 14 j": 336, "tous les 7 j": 168}


def ajuster(X, y, debut, fin):
    """Entraîne un modèle linéaire sur les heures [debut, fin)."""
    return Ridge(alpha=1.0).fit(X[debut:fin], y[debut:fin])


def injecter(X, y, type_derive, intensite, sigma):
    """Ajoute une dérive à la température y (X ne change pas : c'est bien un changement de relation).
    sigma = erreur typique du modèle ; intensite = taille de la dérive en multiples de sigma."""
    y = y.copy()
    if type_derive == "aucune":
        return y
    apres = np.arange(len(y)) >= T0
    if type_derive == "saut":                 # la température monte d'un coup
        y[apres] += intensite * sigma
    elif type_derive == "relation":           # la température réagit plus fort à la charge HUFL
        z = (X[:, 0] - X[:672, 0].mean()) / X[:672, 0].std()
        y[apres] += intensite * sigma * z[apres]
    else:
        raise ValueError(type_derive)
    return y


def sigma_reference(X, y):
    """Erreur typique du modèle initial sur les 2 semaines qui suivent son entraînement (672 à 1008)."""
    m = ajuster(X, y, 0, DEBUT_MODELE)
    return (y[672:1008] - m.predict(X[672:1008])).std()


def prochain_reentrainement(X, y, modele, b, strategie, h):
    """Instant du prochain réentraînement (ou None). b = instant où le modèle actuel est entré en service."""
    n = len(y)
    if strategie == "jamais":
        return None
    if strategie in PERIODES:
        t = b + PERIODES[strategie]
        return t if t < n else None
    if strategie == "oracle":
        t = T0 + ATTENTE
        return t if (b < t < n) else None
    # "sur alerte" : CUSUM sur l'erreur du modèle actuel, à partir de b
    e = y[b:] - modele.predict(X[b:])
    alertes = [b + t for t in cusum(e, h=h, debut=0) if b + t >= ZONE]
    if not alertes:
        return None
    t = alertes[0] + ATTENTE
    return t if t < n else None


def simuler(X, y, strategie, h=20.0):
    """Renvoie (erreurs absolues heure par heure, liste des instants de réentraînement)."""
    n = len(y)
    b = DEBUT_MODELE
    modele = ajuster(X, y, 0, b)
    erreurs = np.full(n, np.nan)
    reentrainements = []
    while True:
        t_suivant = prochain_reentrainement(X, y, modele, b, strategie, h)
        fin = n if t_suivant is None else t_suivant
        erreurs[b:fin] = np.abs(y[b:fin] - modele.predict(X[b:fin]))
        if t_suivant is None:
            break
        modele = ajuster(X, y, t_suivant - FENETRE, t_suivant)
        reentrainements.append(t_suivant)
        b = t_suivant
    return erreurs, reentrainements