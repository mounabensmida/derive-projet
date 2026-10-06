import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from river import drift
from src.generateur import generer_serie
from src.residus import residus, standardiser, DEBUT, LONG_REF
from src.detecteurs_stat import page_hinkley, cusum, ks_glissant, mw_glissant


def premiere_alerte_river(detecteur, z):
    for t in range(DEBUT + LONG_REF, len(z)):
        detecteur.update(z[t])
        if detecteur.drift_detected:
            return t
    return None


s, t0 = generer_serie(seed=1, type_derive="saut_moyenne", intensite=2.0)
x = residus(s)
z = standardiser(x)

def premiere(alertes):
    return alertes[0] if alertes else None

print("Vraie rupture : t0 =", t0)
print("Mes détecteurs :")
print("  Page-Hinkley :", premiere(page_hinkley(x)))
print("  CUSUM        :", premiere(cusum(x)))
print("  KS glissant  :", premiere(ks_glissant(x)))
print("  MW glissant  :", premiere(mw_glissant(x)))
print("river :")
print("  ADWIN        :", premiere_alerte_river(drift.ADWIN(), z))
print("  KSWIN        :", premiere_alerte_river(drift.KSWIN(alpha=1e-4, window_size=200, stat_size=50, seed=42), z))

# Mes détecteurs :
#   Page-Hinkley : 1706
#   CUSUM        : 1688
#   KS glissant  : 1732
#   MW glissant  : 1371
# river :
#   ADWIN        : 1711
#   KSWIN        : 1413
