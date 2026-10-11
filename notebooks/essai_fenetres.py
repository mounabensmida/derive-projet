import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.detecteurs_deep import fabriquer_fenetres, lisser

z = np.arange(100, dtype=float)
instants, X, y = fabriquer_fenetres(z, 30, 50)
print(X.shape)       # (20, 24) : 20 fenêtres de 24 valeurs
print(X[0][:3], y[0])  # [6. 7. 8.] 30.0 : la valeur à t=30, et les 24 avant (6 à 29)

print(lisser(np.array([1., 2., 3., 4.]), k=2))   # [nan 1.5 2.5 3.5]