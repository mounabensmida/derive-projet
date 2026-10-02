import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

# rng = np.random.default_rng(42)   # 42 = la graine du hasard (résultats reproductibles)

# # --- Partie A : série AVEC dérive ---
# avant = rng.normal(loc=0, scale=1, size=500)
# apres = rng.normal(loc=3, scale=1, size=500)
# serie = np.concatenate([avant, apres])
# stat, p = ks_2samp(serie[:500], serie[500:])
# print("AVEC dérive -> statistique :", round(stat, 3), "| p-value :", p)

# # --- Partie B : série CALME (sans dérive) ---
# calme = rng.normal(0, 1, 1000)
# stat, p = ks_2samp(calme[:500], calme[500:])
# print("SANS dérive -> statistique :", round(stat, 3), "| p-value :", round(p, 3))

# if p < 0.01:
#     print("Décision : ALERTE")
# else:
#     print("Décision : pas d'alerte")

# # --- Partie C : répéter 10 fois pour voir que p varie avec le hasard ---
# print("\n10 séries calmes différentes :")
# nb_alertes = 0
# for graine in range(10):
#     s = np.random.default_rng(graine).normal(0, 1, 1000)
#     _, p = ks_2samp(s[:500], s[500:])
#     verdict = "ALERTE" if p < 0.01 else "ok"
#     nb_alertes += (p < 0.01)
#     print(f"  graine {graine} : p = {p:.3f}  -> {verdict}")
# print("Fausses alertes :", nb_alertes, "sur 10")

# # --- Partie D : graphique ---
# fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
# axes[0].plot(serie, lw=0.7)
# axes[0].axvline(500, color="red", ls="--")
# axes[0].set_title("Série AVEC dérive")
# axes[1].plot(calme, lw=0.7, color="green")
# axes[1].axvline(500, color="red", ls="--")
# axes[1].set_title("Série CALME (sans dérive)")
# plt.tight_layout()
# plt.show()


#Version avec la fonction detecteur_ks
# 1) On refabrique les mêmes séries qu'avant (même graine, même ordre)

rng = np.random.default_rng(42)
avant = rng.normal(0,1,500)
apres = rng.normal(3,1,500)
serie = np.concatenate([avant,apres])
calme = rng.normal(0,1,1000) 
#normal est une fonction de la librairie numpy qui permet de générer des nombres aléatoires suivant une distribution normale (ou gaussienne). 
# Elle prend trois arguments : la moyenne (loc), l'écart type (scale) et le nombre d'échantillons à générer (size).
#  Dans ce cas, on génère 1000 échantillons suivant une distribution normale centrée en 0 avec un écart type de 1.
#ecar type =1 cad des valeurs sont entre -1 et +1 de 0

# 2) Le détecteur à fenêtre glissante

def detecteur_ks(serie, taille_fenetre=100, seuil=0.01):
    """
    Détecte les dérives dans une série temporelle en utilisant le test de Kolmogorov-Smirnov.
    Compare la fenêtre courante à une fenêtre de référence (les premiers points)

    Args:
        serie (np.ndarray): La série temporelle à analyser.
        taille_fenetre (int): La taille de la fenêtre pour comparer les distributions.
        seuil (float): Le seuil de p-value pour déclencher une alerte.
        
    Returns:
        list: Une liste d'indices où des dérives ont été détectées.
    """
    alerts = []
    reference = serie[:taille_fenetre]
    for i in range (2*taille_fenetre,len(serie))  :
        #i=100 (de 0 a 99) i =150 il va prendre de 50 a 150 tjs le 100 dernier points
        #C'est pour ça qu'on commence à t = 200 = 2 × 100.
        #  C'est le premier instant où la fenêtre courante est entièrement composée de nouveaux points.
        courant = serie[i-taille_fenetre:i]  # les 100 derniers points vus
        _, p = ks_2samp(reference, courant)
        if p < seuil:
            alerts.append(i)

    return alerts

# 3) Test sur la série AVEC dérive
alerts = detecteur_ks(serie)
premiere = alerts[0]
print("Première alerte à t =", premiere)
print("Délai de détection  =", premiere - 500, "points")
# 4) Test sur la série CALME
alerts_calme = detecteur_ks(calme)
print("Alertes sur la série calme :", len(alerts_calme))

# Répétons sur 5 séries calmes différentes  découvrir le problème des fausses alertes
for j in range(5):
    s= np.random.default_rng(j).normal(0,1,1000) # cette ligne génère une nouvelle série de 1000 points suivant une distribution normale centrée en 0 avec un écart type de 1, en utilisant une graine différente (j) pour chaque itération.
    print("graine",j,"->",len(detecteur_ks(s)), "fausse alertes") # cette ligne applique le détecteur de dérives à la nouvelle série générée et affiche le nombre de fausses alertes détectées pour cette série.
# 5) Graphique
plt.figure(figsize=(10, 4))
plt.plot(serie, lw=0.7)
plt.axvline(500, color="red", ls="--", label="vraie dérive (t=500)")
plt.axvline(premiere, color="green", ls="--", label=f"première alerte (t={premiere})")
plt.legend()
plt.title("Détecteur à fenêtre glissante")
plt.show()

#resultat
#  Première alerte à t = 513
# Délai de détection  = 13 points  513-500
# Alertes sur série calme : 10 c est inutile car ca devient le normale qu on a voire de valeur comme ca car la moy de valeur a augmenter depuis 513