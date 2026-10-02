"""Générateur de séries synthétiques avec dérive."""
import numpy as np

SIGMA = 5.0 # l ecart type de la série synthétique
TYPES_DERIVE = ["saut_moyenne", "graduelle", "variance", "saisonnalite", "forme"]

def bruit_ar1(n, phi, sigma, rng):  #La force de la mémoire (de 0 à 1)
    """Bruit avec mémoire : chaque valeur dépend un peu de la précédente.
    (plus réaliste qu'un bruit où chaque point est indépendant)"""
    e= rng.normal(0, 1, n) #n est le nombre de points de la série
    x = np.zeros(n) #x est un tableau de n zéros
    #sachant Une série énergétique réaliste = niveau + cycle journalier + cycle hebdomadaire + bruit
    for i in range(1, n):
        x[i] = phi * x[i-1] + sigma * e[i] # en remplaçant x[i-1] par la valeur précédente, on introduit une dépendance entre les points de la série.
        
    return x * sigma / x.std() #fait un réglage de volume : elle remet l'agitation exactement à sigma


def generer_serie(n=3360, seed=0, type_derive=None, t0=None,
                    intensite=1.0, duree=200):
                    """n=3360 points = 20 semaines de mesures horaires.intensite : force de la dérive.
                    - saut_moyenne / graduelle : en multiples de l'écart-type du bruit
                    - variance / saisonnalite   : en proportion (1.0 = +100 %)
                        Retourne (serie, t0)."""
                    rng = np.random.default_rng(seed) #seed est le point de départ de la génération aléatoire, pour pouvoir reproduire les mêmes résultats.
                    t = np.arange(n) #t est un tableau de n points allant de 0 à n-1
                    niveau = np.full(n, 100.0) #niveau est un tableau de n points tous égaux à 100.0
                    saison_jour = 20 * np.sin(2 * np.pi * t / 24) #cycle journalier autrement dis c est une sinusoïde de période 24 heures et d'amplitude 20
                    saison_semaine = 10 * np.sin(2 * np.pi * t / 168) #cycle hebdomadaire autrement dis c est une sinusoïde de période 168
                    bruit = bruit_ar1(n, 0.6, SIGMA, rng) #bruit est un tableau de n points généré par la fonction bruit_ar1 avec une mémoire de 0.6 et un écart-type de SIGMA

                    if type_derive is not None :
                        if t0 is None :
                            t0 = n // 2 #si t0 n est pas précisé, il est mis au milieu de la série
                            if type_derive == "saut_moyenne" :
                                niveau[t0:] += intensite * SIGMA #on ajoute un saut de moyenne à partir de t0
                            elif type_derive == "graduelle" :
                                delta = intensite * SIGMA  #on ajoute une dérive graduelle à partir de t0
                                niveau[t0:t0+duree] += np.linspace(0, delta, duree) #linespace crée un tableau de duree points allant de 0 à delta 
                                niveau[t0+duree:] += delta #on ajoute delta à partir de t0+duree
                            elif type_derive == "variance" :
                                bruit[t0:] *= (1 + intensite) #on multiplie le bruit par 1+intensite  à partir de t0
                            elif type_derive == "saisonnalite":
                                saison_jour[t0:] *= (1 + intensite)
                            elif type_derive == "forme":
                                # même écart-type, mais queues plus lourdes (loi de Student, 3 ddl)
                                lourd = rng.standard_t(df=3, size=n - t0) / np.sqrt(3) * SIGMA
                                bruit[t0:] = lourd
                            else :
                                raise ValueError(f"type inconnu : {type_derive}")

                    serie = niveau + saison_jour + saison_semaine + bruit
                    return serie, t0

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