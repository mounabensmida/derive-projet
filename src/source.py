"""D'où vient la série qu'on rejoue ? Synthétique (avec dérive injectée) ou réelle (jeu ETT, dérive injectée)."""
import os
from src.generateur import generer_serie
from src.injection import injecter, T0
from src.donnees_reelles import charger, LONGUEUR, DEBUTS_TEST, DOSSIER

TYPES = ["aucune", "saut_moyenne", "graduelle", "variance", "saisonnalite", "forme"]


def donnees_reelles_presentes():
    return os.path.exists(os.path.join(DOSSIER, "ETTh1.csv"))


def construire_serie(source="synthétique", type_derive="saut_moyenne", intensite=2.0, graine=0):
    """Renvoie (série, instant de la dérive ou None)."""
    if source == "réelle":
        debut = DEBUTS_TEST[graine % len(DEBUTS_TEST)]
        s = charger("ETTh1", "HUFL")[debut:debut + LONGUEUR]
        if type_derive == "aucune":
            return s, None
        return injecter(s, type_derive, intensite, graine=graine), T0
    if type_derive == "aucune":
        return generer_serie(seed=graine)[0], None
    return generer_serie(seed=graine, type_derive=type_derive, intensite=intensite)


def reglages(source):
    from src.streaming import REGLAGES_REEL, REGLAGES_SYNTHETIQUE
    return REGLAGES_REEL if source == "réelle" else REGLAGES_SYNTHETIQUE