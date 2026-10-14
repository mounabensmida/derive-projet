.PHONY: install data test demo run bench4 bench5 analyse reproduire propre

install:            ## installer les bibliothèques
	python -m pip install -r requirements.txt

data:               ## télécharger les données réelles (jeu ETT)
	python scripts/telecharger_donnees.py

test:               ## lancer tous les tests
	python -m pytest -q

demo:               ## démo en terminal (streaming simulé)
	python notebooks/demo_streaming.py

run: data           ## ouvrir le tableau de bord (http://localhost:8501)
	streamlit run dashboard.py

bench4:             ## benchmark de la semaine 4 (1440 séries, environ 5 à 20 min)
	python notebooks/bench_semaine4.py 30 2

bench5:             ## benchmarks de la semaine 5 (données réelles, environ 4 min)
	python notebooks/bench_semaine5_detection.py
	python notebooks/bench_semaine5_reentrainement.py

analyse:            ## tableaux et figures
	python notebooks/analyse_semaine4.py
	python notebooks/analyse_semaine5_detection.py
	python notebooks/analyse_semaine5_reentrainement.py

reproduire: install data test bench4 bench5 analyse   ## tout refaire d'une seule commande

propre:             ## supprimer les résultats calculés
	rm -f resultats_*.csv reglages_*.json