"""Données réelles : charge électrique horaire de transformateurs (jeu ETT).
On découpe les 2 ans de mesures en 'séries' de 3360 heures (comme nos séries synthétiques)."""
import os
import numpy as np
import pandas as pd

DOSSIER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
COLONNES = ["HUFL", "MUFL", "LUFL"]      # trois mesures de charge utile
LONGUEUR = 3360                          # 20 semaines, comme la série synthétique
PAS = 1680                               # une nouvelle fenêtre toutes les 10 semaines


def charger(fichier, colonne):
    """Renvoie la série horaire (tableau numpy) d'une colonne d'un fichier ETT."""
    d = pd.read_csv(os.path.join(DOSSIER, fichier + ".csv"))
    return d[colonne].to_numpy(dtype=float)


def decouper(fichier, colonne):
    """Découpe en fenêtres de 3360 h, décalées de 1680 h. Renvoie une liste de tableaux."""
    x = charger(fichier, colonne)
    return [x[d:d + LONGUEUR] for d in range(0, len(x) - LONGUEUR + 1, PAS)]


def toutes_les_fenetres(fichier):
    """[(identifiant, fenêtre), ...] pour les 3 colonnes d'un fichier."""
    out = []
    for col in COLONNES:
        for k, w in enumerate(decouper(fichier, col)):
            out.append((f"{fichier}-{col}-{k}", w))
    return out


# ---------- Partie "prévision"  ----------
CHARGES = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL"]   # 6 mesures de charge (les "entrées")
CIBLE = "OT"                                                   # température de l'huile (ce qu'on prévoit)
DEBUTS_CALIBRATION = list(range(0, 3361, 840))        # fenêtres du "passé"   : heures 0 à 6720
DEBUTS_TEST = list(range(6720, 14001, 840))           # fenêtres du "futur"   : à partir de l'heure 6720


def fenetres_prevision(fichier, debuts):
    """Liste de (X, y) : X = 6 charges + heure du jour (sin, cos), y = température. 3360 h chacune."""
    d = pd.read_csv(os.path.join(DOSSIER, fichier + ".csv"), parse_dates=["date"])
    h = d["date"].dt.hour.to_numpy()
    X = np.column_stack([d[CHARGES].to_numpy(float), np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24)])
    y = d[CIBLE].to_numpy(float)
    return [(X[s:s + LONGUEUR].copy(), y[s:s + LONGUEUR].copy()) for s in debuts]


# ---------- Partie "détection"  ----------
def fenetres_detection(fichier, debuts):
    """[(identifiant, fenêtre de 3360 h), ...] pour les 3 colonnes de charge utile."""
    out = []
    for col in COLONNES:
        x = charger(fichier, col)
        for s in debuts:
            out.append((f"{col}-{s}", x[s:s + LONGUEUR].copy()))
    return out