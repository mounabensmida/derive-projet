from scipy.stats import ks_2samp

def detecteur_ks(serie, taille_fenetre=168, seuil=0.01):
    """Détecteur basé sur le test de Kolmogorov-Smirnov.
    Retourne la liste des instants d'alerte."""
    alertes = []
    reference = serie[:taille_fenetre]  # on prend la première fenêtre comme référence
    for t in range(taille_fenetre, len(serie) ):
        fenetre = serie[t-taille_fenetre:t]
        _, p = ks_2samp(reference, fenetre)  # test de Kolmogorov-Smirnov
        if p < seuil:
            alertes.append(t)
    return alertes