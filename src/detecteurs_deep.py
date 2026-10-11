"""Détecteurs appris : ils apprennent le 'normal', puis alertent quand le réseau se trompe."""
import numpy as np
from src.residus import standardiser 

FENETRE = 24                 # le réseau regarde 24 heures d'un coup
ENTRAINEMENT = (672, 1008)   # période NORMALE sur laquelle le réseau apprend
VALIDATION = (1008, 1344)    # période NORMALE (autre) pour fixer le seuil
DEBUT_DEEP = 1344            # la détection commence ici
LISSAGE = 24                 # on lisse l'erreur sur 24 heures (évite les alertes sur un seul point)


_MEMOIRE = {}                # garde les scores pour ne pas réentraîner à chaque seuil

def fabriquer_fenetres(z, t_debut, t_fin, taille=FENETRE):
    """Pour chaque instant t : (les 24 valeurs avant t, la valeur à t)."""
    instants = np.arange(t_debut, t_fin) #: la liste des instants ( 696, 697, …)
    X = np.array([z[t - taille:t] for t in instants])#les 24 valeurs juste avant t
    y = z[instants]
    return instants, X, y

def lisser(scores, k=LISSAGE):
    """Moyenne glissante causale : chaque point = moyenne des k derniers scores.
    Une seule grosse erreur isolée ne doit pas déclencher une alerte."""
    cumul = np.cumsum(np.insert(scores, 0, 0.0))
    # np.cumsum calcule les sommes cumulées : on obtient une moyenne glissante rapidement, sans boucle.
    lisses = np.full(len(scores), np.nan)
    lisses[k - 1:] = (cumul[k:] - cumul[:-k]) / k
    return lisses


def calculer_scores(serie, nom_modele, fabrique):
    """Entraîne le réseau sur la période normale, puis note chaque instant. Renvoie un tableau."""
    cle = (nom_modele, hash(serie.tobytes()))
    if cle in _MEMOIRE:
        return _MEMOIRE[cle]
    z = standardiser(serie)
    modele = fabrique() #on crée un réseau neuf
    _, X_ent, y_ent = fabriquer_fenetres(z, ENTRAINEMENT[0] + FENETRE, ENTRAINEMENT[1])
    modele.apprendre(X_ent, y_ent)
    instants, X, y = fabriquer_fenetres(z, FENETRE, len(z))
    bruts = np.full(len(z), np.nan)
    bruts[instants] = modele.erreurs(X, y)
    scores = lisser(np.nan_to_num(bruts)) #on moyenne l'erreur sur 24 heures.
    scores[:FENETRE + LISSAGE] = np.nan  # .nan les premiers points n'ont pas assez d'historique, on les efface.
    _MEMOIRE[cle] = scores
    return scores

def alertes_depuis_scores(scores, marge):
    """Seuil = marge x le pire score vu pendant la période normale de validation."""
    pire_normal = np.nanmax(scores[VALIDATION[0] + FENETRE + LISSAGE:VALIDATION[1]])
    seuil = marge * pire_normal
    return [t for t in range(DEBUT_DEEP, len(scores)) if scores[t] > seuil]

class SansReseau:
    """Contrôle : aucun apprentissage. Le 'score' est juste la valeur au carré."""
    def apprendre(self, X, y):
        pass

    def erreurs(self, X, y):
        return y ** 2