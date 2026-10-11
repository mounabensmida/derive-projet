import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.modeles_torch import AutoEncodeur

X = np.random.default_rng(0).normal(0, 1, (200, 24))   # du bruit "normal"
modele = AutoEncodeur(epoques=300)
print("Erreur AVANT apprentissage :", modele.erreurs(X).mean())
modele.apprendre(X)
print("Erreur APRÈS apprentissage :", modele.erreurs(X).mean())
X_bizarre = X * 3                                       # des valeurs 3 fois plus agitées
print("Erreur sur des données bizarres :", modele.erreurs(X_bizarre).mean())