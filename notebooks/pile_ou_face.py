import numpy as np

rng = np.random.default_rng(0)
VRAI_TAUX = 0.70        # imaginons qu'un détecteur voie vraiment la dérive 7 fois sur 10

for n in [10, 30, 90, 300]:
    # on répète 1000 fois l'expérience "tester le détecteur sur n séries"
    mesures = [(rng.random(n) < VRAI_TAUX).mean() for _ in range(1000)]
    bas, haut = np.percentile(mesures, [2.5, 97.5])
    print(f"avec {n:3d} séries : on mesure entre {bas:.0%} et {haut:.0%}   (la vérité est 70 %)")