Les règles :

Un détecteur reçoit une série et retourne la liste des instants d'alerte.
On connaît la vraie rupture t0.
Une alerte est bonne si elle tombe dans la fenêtre [t0, t0 + tolérance] (on prend tolérance = 300 heures).
Une alerte avant t0 est une fausse alerte.
Le délai = (première bonne alerte) − t0.
Si aucune alerte dans la fenêtre : détection manquée.