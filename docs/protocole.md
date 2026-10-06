# Les règles :

Un détecteur reçoit une série et retourne la liste des instants d'alerte.
On connaît la vraie rupture t0.
Une alerte est bonne si elle tombe dans la fenêtre [t0, t0 + tolérance] (on prend tolérance = 300 heures).
Une alerte avant t0 est une fausse alerte.
Le délai = (première bonne alerte) − t0.
Si aucune alerte dans la fenêtre : détection manquée.


# Protocole d'évaluation, v1

## 1. Problème
Les modèles de prévision de consommation énergétique perdent en
précision quand le comportement des données change (nouvelle machine,
nouvelle règle, événement climatique). Ce changement s'appelle la dérive.
Objectif : détecter la dérive vite, avec peu de fausses alertes.

## 2. Types de dérive simulés
| Type           | Ce qui change                               |
|---             |---                                          |
| saut_moyenne   | le niveau monte d'un coup                   |
| graduelle      | le niveau monte sur 200 heures              |
| variance       | le bruit devient plus agité                 |
| saisonnalite   | le cycle jour/nuit s'amplifie               |
| forme          | mêmes écarts, mais plus de valeurs extrêmes |

## 3. Données
Série horaire de 3 360 points (20 semaines) =
niveau (100) + cycle 24 h + cycle 168 h + bruit AR(1) (phi = 0,6,
écart-type 5). Une dérive est injectée à t0 = 1 680 (milieu de la série).

## 4. Règles d'évaluation
- Un détecteur retourne la liste de ses instants d'alerte.
- Alerte avant t0 = fausse alerte.
- Première alerte dans [t0, t0 + 300] = détection ; délai = alerte - t0.
- Aucune alerte dans cette fenêtre = détection manquée.

## 5. Métriques
Taux de détection, délai moyen, nombre de fausses alertes (moyennes
sur 10 graines par type de dérive).

## 6. Limites connues
Données synthétiques ; 10 graines seulement ; un seul niveau
d'intensité ; fausses alertes évaluées sur la partie avant t0.

## 7. Prochaines étapes
Semaine 2 : Page-Hinkley, CUSUM, Mann-Whitney sur le même banc d'essai.



## remarque sue le redu 
ref[k::periode] : prend les points k, k+168, k+336, k+504 : « le même créneau horaire de la semaine, chaque semaine ». On en fait la moyenne.

np.arange(len(serie)) % periode : donne pour chaque point son créneau (0 à 167). % est le reste de la division : le point 170 est au créneau 2 (170 − 168).

standardiser : retire la moyenne et divise par l'écart-type calculés sur la référence : le résultat s'exprime en « agitations normales ».

## Je suppose dans cette méthode  qu'on connaît la période (168 h) !!!!
Remarque :
Si les 4 premières semaines contenaient déjà une dérive, le profil serait-il bon ?
Non, il serait faussé. Le profil doit être appris sur une période normale.