"""Modèles de secours (si PyTorch ne s'installe pas). Même interface que modeles_torch."""
import numpy as np
from sklearn.neural_network import MLPRegressor


class AutoEncodeur:
    def apprendre(self, X, y=None):
        self.m = MLPRegressor(hidden_layer_sizes=(8,), activation="tanh",
                            max_iter=600, random_state=0)
        self.m.fit(X, X)                      # le réseau apprend à recopier son entrée

    def erreurs(self, X, y=None):
        return ((self.m.predict(X) - X) ** 2).mean(axis=1)


class PredicteurMLP:
    def apprendre(self, X, y):
        self.m = MLPRegressor(hidden_layer_sizes=(16,), activation="tanh",
                            max_iter=600, random_state=0)
        self.m.fit(X, y)                      # 24 valeurs passées -> la valeur suivante

    def erreurs(self, X, y):
        return np.abs(self.m.predict(X) - y)