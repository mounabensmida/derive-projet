import numpy as np
import matplotlib.pyplot as plt

def bruit_ar1(n, phi, sigma, rng):
    """Bruit avec mémoire : chaque valeur dépend un peu de la précédente."""
    e = rng.normal(0, 1, n)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x * sigma / x.std()

rng = np.random.default_rng(0)
bruit_memoire = bruit_ar1(500, 0.6, 5, rng)   # bruit AVEC mémoire
bruit_simple = rng.normal(0, 5, 500)          # bruit SANS mémoire

print("Écart-type avec mémoire :", round(bruit_memoire.std(), 2))
print("Écart-type sans mémoire :", round(bruit_simple.std(), 2))
corr_m = np.corrcoef(bruit_memoire[:-1], bruit_memoire[1:])[0, 1]
corr_s = np.corrcoef(bruit_simple[:-1], bruit_simple[1:])[0, 1]
print("Mémoire (corrélation) avec :", round(corr_m, 2))
print("Mémoire (corrélation) sans :", round(corr_s, 2))

fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True, sharey=True)
axes[0].plot(bruit_simple, lw=0.8)
axes[0].set_title("Bruit simple : rng.normal(0, 5, 500)")
axes[1].plot(bruit_memoire, lw=0.8, color="green")
axes[1].set_title("Bruit avec mémoire : bruit_ar1(500, 0.6, 5, rng)")
plt.tight_layout()
plt.show()