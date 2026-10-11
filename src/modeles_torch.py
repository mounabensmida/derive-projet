"""Modèles PyTorch : un auto-encodeur et un prédicteur. Même interface que modeles_sklearn."""
import numpy as np
import torch
from torch import nn


def _entrainer(reseau, X, cible, epoques, pas):
    optimiseur = torch.optim.Adam(reseau.parameters(), lr=pas)
    perte = nn.MSELoss()
    reseau.train()
    for _ in range(epoques):
        optimiseur.zero_grad()
        perte(reseau(X), cible).backward()
        optimiseur.step()
    reseau.eval()


def _tenseur(a):
    return torch.as_tensor(np.asarray(a), dtype=torch.float32)


class AutoEncodeur:
    def __init__(self, taille=24, cachees=8, epoques=300, pas=0.01, graine=0):
        torch.manual_seed(graine)
        self.epoques, self.pas = epoques, pas
        self.m = nn.Sequential(nn.Linear(taille, cachees), nn.Tanh(),
                            nn.Linear(cachees, taille))

    def apprendre(self, X, y=None):
        X = _tenseur(X)
        _entrainer(self.m, X, X, self.epoques, self.pas)   # le réseau apprend à recopier son entrée

    def erreurs(self, X, y=None):
        X = _tenseur(X)
        with torch.no_grad():
            return ((self.m(X) - X) ** 2).mean(dim=1).numpy()


class PredicteurMLP:
    def __init__(self, taille=24, cachees=16, epoques=300, pas=0.01, graine=0):
        torch.manual_seed(graine)
        self.epoques, self.pas = epoques, pas
        self.m = nn.Sequential(nn.Linear(taille, cachees), nn.Tanh(),
                            nn.Linear(cachees, 1))

    def apprendre(self, X, y):
        # 24 valeurs passées -> la valeur suivante
        _entrainer(self.m, _tenseur(X), _tenseur(y).reshape(-1, 1), self.epoques, self.pas)

    def erreurs(self, X, y):
        with torch.no_grad():
            return np.abs(self.m(_tenseur(X)).numpy().ravel() - np.asarray(y))


class _ReseauLSTM(nn.Module):
    def __init__(self, cachees):
        super().__init__()
        self.lstm = nn.LSTM(1, cachees, batch_first=True)
        self.sortie = nn.Linear(cachees, 1)

    def forward(self, X):
        etats, _ = self.lstm(X.unsqueeze(-1))     # (n, 24) -> (n, 24, 1) : une valeur par heure
        return self.sortie(etats[:, -1])          # on prédit à partir du dernier état


class PredicteurLSTM:
    def __init__(self, cachees=16, epoques=200, pas=0.01, graine=0):
        torch.manual_seed(graine)
        self.epoques, self.pas = epoques, pas
        self.m = _ReseauLSTM(cachees)

    def apprendre(self, X, y):
        # 24 valeurs passées, lues dans l'ordre -> la valeur suivante
        _entrainer(self.m, _tenseur(X), _tenseur(y).reshape(-1, 1), self.epoques, self.pas)

    def erreurs(self, X, y):
        with torch.no_grad():
            return np.abs(self.m(_tenseur(X)).numpy().ravel() - np.asarray(y))
