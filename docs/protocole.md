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

## KS Vs. Mann-Whitney « KS voit la forme, MW voit le niveau »
KS	 La forme complète des deux paquets
MW	Si un paquet a tendance à avoir des valeurs plus grandes

## par rapport fenetre glissant
La référence ne commence plus à 0 mais à debut (t = 672).
_fenetre_glissante est une fonction commune : on lui passe le test voulu. Même squelette, deux tests, aucun copier-coller (bonne pratique).
Le seuil par défaut devient 1e-5.

## la calibration

Problème : chaque détecteur a un réglage de sensibilité (seuil p pour KS/MW, h pour CUSUM, seuil pour PH). Si on compare un détecteur réglé « nerveux » à un autre réglé « prudent », le nerveux paraît meilleur en vitesse mais fait plus de fausses alertes. La comparaison est truquée.

Solution : régler chacun pour avoir à peu près le même niveau de fausses alertes sur des séries calmes. On fixe une cible : « au plus 10 % des séries calmes ont une fausse alerte ». On choisit alors le réglage le plus sensible qui respecte la cible.


## resultat 
Calibration : KS brut
  réglage 0.01 : 0% de séries calmes avec fausse alerte
Calibration : KS résidus
  réglage 0.01 : 95% de séries calmes avec fausse alerte
  réglage 0.001 : 70% de séries calmes avec fausse alerte  réglage 0.0001 : 35% de séries calmes avec fausse alerte
  réglage 1e-05 : 10% de séries calmes avec fausse alerteCalibration : MW résidus
  réglage 0.01 : 100% de séries calmes avec fausse alerte  réglage 0.001 : 80% de séries calmes avec fausse alerte  réglage 0.0001 : 50% de séries calmes avec fausse alerte
  réglage 1e-05 : 20% de séries calmes avec fausse alerte  réglage 1e-06 : 10% de séries calmes avec fausse alerteCalibration : PH résidus
  réglage 10 : 100% de séries calmes avec fausse alerte
  réglage 15 : 95% de séries calmes avec fausse alerte
  réglage 20 : 50% de séries calmes avec fausse alerte
  réglage 25 : 25% de séries calmes avec fausse alerte
  réglage 30 : 15% de séries calmes avec fausse alerte
  réglage 40 : 5% de séries calmes avec fausse alerte
Calibration : CUSUM résidus
  réglage 10 : 100% de séries calmes avec fausse alerte
  réglage 15 : 90% de séries calmes avec fausse alerte
  réglage 20 : 65% de séries calmes avec fausse alerte
  réglage 25 : 35% de séries calmes avec fausse alerte
  réglage 30 : 20% de séries calmes avec fausse alerte
  réglage 40 : 0% de séries calmes avec fausse alerte

Seuils choisis : {'KS brut': 0.01, 'KS résidus': 1e-05, 'MW résidus': 1e-06, 'PH résidus': 40, 'CUSUM résidus': 40} 

methode       CUSUM résidus  KS brut  KS résidus  MW résidus  PH résidus
type                                                                    
forme                   0.0      0.0         0.0         0.0         0.0
graduelle               1.0      1.0         1.0         1.0         1.0
saisonnalite            1.0      1.0         1.0         0.0         1.0
saut_moyenne            1.0      1.0         1.0         1.0         1.0
variance                0.8      0.1         0.9         0.0         0.8

methode       CUSUM résidus  KS brut  KS résidus  MW résidus  PH résidus
type                                                                    
forme                   NaN      NaN         NaN         NaN         NaN
graduelle            133.10    190.3      139.80       134.2      147.90
saisonnalite          10.20     71.7      102.10         NaN       10.40
saut_moyenne          31.50     92.4       54.90        55.7       35.20
variance              66.38    248.0      168.33         NaN       68.25

Durée : 713 s

Retirer le cycle a fait passer KS de 10 % à 90 % sur la variance.
MW ne voit que le niveau.
Personne ne voit la dérive de forme.

Les 4 conclusions à retenir
1-Retirer le cycle aide beaucoup. Variance : KS brut 10 % contre KS résidus 90 %.
2-Chaque détecteur a un point aveugle. MW ne voit que le niveau (pas la variance, pas la saisonnalité), donc 0 % à ces deux endroits. Ce n'est pas un bug.
3-CUSUM et Page-Hinkley sont les plus rapides. Un compteur réagit dès les premiers points, alors qu'une fenêtre doit d'abord se remplir.
4-Aucune méthode ne voit la dérive de "forme". Ce n'est pas un échec : c'est un résultat qui prépare la semaine 3.