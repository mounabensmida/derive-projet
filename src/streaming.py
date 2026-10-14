"""Streaming simulé : on REJOUE une série point par point, comme si elle arrivait en direct.

Règle d'or : à l'instant t, le moteur n'a vu QUE les points 0 à t. Il n'a jamais accès au futur.

Calendrier (le même que pour les benchmarks) :
    0 - 672      le moteur apprend le profil de la semaine type
    672 - 1008   période de référence (on mesure le "normal")  ; le réseau apprend ici
    1008 - 1344  validation : on fixe le seuil du réseau
    1344 -       surveillance : les alertes comptent."""
import numpy as np
from sklearn.neural_network import MLPRegressor

PERIODE = 168       # une semaine
N_PROFIL = 672      # 4 semaines pour apprendre le profil
DEBUT_REF = 672     # début de la référence
FIN_REF = 1008      # fin de la référence (début de la surveillance de CUSUM)
FIN_VALID = 1344    # fin de la validation du réseau
FEN = 24            # le réseau regarde 24 h
LISSAGE = 24

REGLAGES_SYNTHETIQUE = {"cusum_h": 20.0, "marge_reseau": 1.5, "marge_controle": 1.5}
REGLAGES_REEL = {"cusum_h": 200.0, "marge_reseau": 1.5, "marge_controle": 2.0}


class MoteurEnLigne:
    """Reçoit les points UN PAR UN (méthode `recevoir`) et calcule 3 scores : CUSUM, réseau, contrôle."""

    def __init__(self, cusum_h=20.0, marge_reseau=1.5, marge_controle=1.5, k=0.5):
        self.h, self.k = cusum_h, k
        self.marges = {"reseau": marge_reseau, "controle": marge_controle}
        self.brut = []            # valeurs brutes reçues
        self.res = []             # résidus (valeur - profil)
        self.z = []               # résidus standardisés
        self.profil = None
        self.moy = self.std = None
        self.s_haut = self.s_bas = 0.0
        self.reseau = None
        self.err = {"reseau": [], "controle": []}      # erreur à chaque instant
        self.score = {"reseau": [], "controle": []}    # erreur lissée sur 24 h
        self.seuil = {"reseau": np.nan, "controle": np.nan}

    # ---------- une étape = un nouveau point ----------
    def recevoir(self, x):
        t = len(self.brut)
        self.brut.append(float(x))
        if t == N_PROFIL:                                   # on connaît 4 semaines : on fixe le profil
            ref = np.array(self.brut[:N_PROFIL])
            self.profil = np.array([ref[k::PERIODE].mean() for k in range(PERIODE)])
            self.res = [self.brut[i] - self.profil[i % PERIODE] for i in range(N_PROFIL)]
        r = np.nan
        if self.profil is not None:
            r = self.brut[t] - self.profil[t % PERIODE]
            self.res.append(r)                              # résidus de 0 à t (ceux d'avant 672 ont été remplis plus haut)
        z = np.nan
        if t == FIN_REF:                                    # la référence est complète : on standardise et on entraîne
            ref = np.array(self.res[DEBUT_REF:FIN_REF])
            self.moy, self.std = ref.mean(), ref.std()
            self.z = [(v - self.moy) / self.std for v in self.res[:FIN_REF]]   # z pour 0..1007
            self._entrainer_reseau()
        if self.moy is not None:
            z = (r - self.moy) / self.std
            if t >= FIN_REF:
                self.z.append(z)                            # z pour 1008, 1009, ...
        sortie = dict(t=t, valeur=float(x), z=z, score_cusum=np.nan, alerte_cusum=False)
        for nom in ("reseau", "controle"):
            sortie[f"score_{nom}"] = np.nan
            sortie[f"seuil_{nom}"] = np.nan
            sortie[f"alerte_{nom}"] = False
        if t >= FIN_REF:
            self._cusum(t, z, sortie)
            for nom in ("reseau", "controle"):
                self._detecteur_erreur(nom, t, sortie)
        return sortie

    # ---------- CUSUM ----------
    def _cusum(self, t, z, sortie):
        self.s_haut = max(0.0, self.s_haut + z - self.k)
        self.s_bas = max(0.0, self.s_bas - z - self.k)
        sortie["score_cusum"] = max(self.s_haut, self.s_bas)
        sortie["alerte_cusum"] = bool(sortie["score_cusum"] > self.h and t >= FIN_VALID)

    # ---------- réseau et contrôle ----------
    def _fenetre(self, a, b):
        return np.array(self.z[a:b])

    def _entrainer_reseau(self):
        """Une seule fois, à l'instant 1008 : le réseau apprend à recopier 24 h de 'normal'."""
        X = np.array([self._fenetre(t - FEN, t) for t in range(DEBUT_REF + FEN, FIN_REF)])
        self.reseau = MLPRegressor(hidden_layer_sizes=(8,), activation="tanh", max_iter=600, random_state=0)
        self.reseau.fit(X, X)

    def _detecteur_erreur(self, nom, t, sortie):
        if nom == "reseau":
            w = self._fenetre(t - FEN, t)
            e = float(((self.reseau.predict(w[None, :]) - w) ** 2).mean())
        else:
            e = float(self.z[t] ** 2)
        liste = self.err[nom]
        while len(liste) < t:                 # avant 1008 : pas de score, on met 0 (comme la version par lots)
            liste.append(0.0)
        liste.append(e)
        sc = float(np.mean(liste[t - LISSAGE + 1:t + 1]))
        self.score[nom].append(sc)
        if t == FIN_VALID - 1:                # la validation se termine : on fixe le seuil
            valide = self.score[nom][1056 - FIN_REF:FIN_VALID - FIN_REF]
            self.seuil[nom] = self.marges[nom] * max(valide)
        sortie[f"score_{nom}"] = sc
        sortie[f"seuil_{nom}"] = self.seuil[nom]
        sortie[f"alerte_{nom}"] = bool(t >= FIN_VALID and sc > self.seuil[nom])


def rejouer(serie, **reglages):
    """Générateur : donne, point par point, ce que voit le moteur."""
    moteur = MoteurEnLigne(**reglages)
    for x in serie:
        yield moteur.recevoir(x)


def premiere_alerte(lignes, nom):
    """Premier instant d'alerte d'un détecteur ('cusum', 'reseau' ou 'controle'), ou None."""
    for r in lignes:
        if r[f"alerte_{nom}"]:
            return r["t"]
    return None