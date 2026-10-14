"""Tableau de bord Streamlit : une série arrive point par point, trois détecteurs surveillent.
Lancer :  streamlit run dashboard.py     (ou : make run)"""
import time
import warnings
warnings.filterwarnings("ignore")
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from src.source import construire_serie, reglages, donnees_reelles_presentes, TYPES
from src.streaming import rejouer

st.set_page_config(page_title="Détection de dérive en direct", layout="wide")
st.title("Détection de dérive conceptuelle : démo en direct")
st.caption("Une série de charge électrique arrive heure par heure. Trois détecteurs la surveillent sans jamais voir le futur. "
        "Avant l'heure 1344, ils apprennent : leurs alertes sont ignorées.")

# ---------------- réglages (barre latérale) ----------------
sources = ["synthétique"] + (["réelle"] if donnees_reelles_presentes() else [])
with st.sidebar:
    st.header("Scénario")
    source = st.radio("Source de la série", sources, help="'réelle' = données ETT (python scripts/telecharger_donnees.py)")
    derive = st.selectbox("Type de dérive injectée", TYPES, index=1)
    intensite = st.slider("Intensité", 1.0, 6.0, 4.0 if source == "réelle" else 2.0, 0.5)
    graine = st.number_input("Graine (change la série)", 0, 99, 0)
    vitesse = st.slider("Vitesse (heures par image)", 6, 120, 48)
    instantane = st.checkbox("Tout afficher d'un coup (sans animation)", value=False)
    lancer = st.button("Lancer la démo", type="primary")
if not donnees_reelles_presentes():
    st.sidebar.info("Données réelles absentes : lancez `python scripts/telecharger_donnees.py` pour activer la source 'réelle'.")


@st.cache_data(show_spinner="Calcul du rejeu (le réseau s'entraîne une fois)...")
def calculer(source, derive, intensite, graine):
    serie, t0 = construire_serie(source, derive, intensite, int(graine))
    lignes = list(rejouer(serie, **reglages(source)))
    return pd.DataFrame(lignes), t0


COULEURS = {"cusum": "#2a78d6", "reseau": "#eb6834", "controle": "#898781"}
NOMS = {"cusum": "CUSUM (niveau)", "reseau": "Autoencodeur (structure)", "controle": "Contrôle sans réseau"}


def courbe(df, colonne, titre, t0, seuil=None, couleur="#2a78d6", nom_alerte=None, hauteur=170):
    """Courbe d'un score. L'axe est plafonné à 3 x le seuil pour que la partie utile reste lisible."""
    haut = 3 * seuil if seuil else None
    y = alt.Y(f"{colonne}:Q", title=titre, scale=alt.Scale(domain=[0, haut], nice=False) if haut else alt.Scale())
    base = alt.Chart(df).encode(x=alt.X("t:Q", title="heure", scale=alt.Scale(domain=[0, 3360])))
    couches = [base.mark_line(color=couleur, strokeWidth=1.6, clip=True).encode(y=y)]
    if seuil is not None:
        couches.append(alt.Chart(pd.DataFrame({"s": [seuil]})).mark_rule(color="#e5484d", strokeDash=[5, 4]).encode(y="s:Q"))
    if t0:
        couches.append(alt.Chart(pd.DataFrame({"x": [t0]})).mark_rule(color="#1baf7a", strokeWidth=2).encode(x="x:Q"))
    if nom_alerte:
        premiere = df[df[f"alerte_{nom_alerte}"]].head(1)
        if len(premiere):
            couches.append(alt.Chart(premiere).mark_rule(color="#e5484d", strokeWidth=2).encode(x="t:Q"))
    return alt.layer(*couches).properties(height=hauteur)


if lancer or instantane or "df" in st.session_state:
    if lancer:
        st.session_state["scenario"] = (source, derive, intensite, graine)
    scenario = st.session_state.get("scenario", (source, derive, intensite, graine))
    df, t0 = calculer(*scenario)
    st.session_state["df"] = True
    n = len(df)
    pas = n if instantane else vitesse
    zone = st.empty()
    for fin in list(range(pas, n, pas)) + [n]:
        vu = df.iloc[:fin]
        with zone.container():
            t = int(vu["t"].iloc[-1])
            c = st.columns(4)
            c[0].metric("Heure", f"{t}")
            etat = []
            for k, nom in enumerate(("cusum", "reseau", "controle")):
                al = vu[vu[f"alerte_{nom}"]]
                c[k + 1].metric(NOMS[nom], "ALERTE" if len(al) else ("surveillance" if t >= 1344 else "apprentissage"),
                                delta=(f"depuis t={int(al['t'].iloc[0])}" if len(al) else None), delta_color="inverse")
            serie = alt.layer(
                alt.Chart(vu).mark_line(color="#4b4b4b", strokeWidth=1).encode(
                    x=alt.X("t:Q", scale=alt.Scale(domain=[0, 3360]), title="heure"), y=alt.Y("valeur:Q", title="charge", scale=alt.Scale(zero=False))),
                *([alt.Chart(pd.DataFrame({"x": [t0]})).mark_rule(color="#1baf7a", strokeWidth=2).encode(x="x:Q")] if t0 else []),
            ).properties(height=190)
            st.caption("La série reçue (trait vert = dérive injectée)")
            st.altair_chart(serie, use_container_width=True)
            h = reglages(scenario[0])["cusum_h"]
            st.caption("Détecteur de niveau : CUSUM. Pointillé rouge = seuil, trait vert = dérive injectée, trait rouge = première alerte.")
            st.altair_chart(courbe(vu, "score_cusum", "score CUSUM", t0, h, COULEURS["cusum"], "cusum"), use_container_width=True)
            for nom, titre in (("reseau", "Détecteur de structure : autoencodeur (erreur de reconstruction lissée)"),
                            ("controle", "Contrôle : même principe, sans réseau")):
                seuil = vu[f"seuil_{nom}"].dropna()
                st.caption(titre)
                st.altair_chart(courbe(vu, f"score_{nom}", "erreur lissée", t0, float(seuil.iloc[-1]) if len(seuil) else None,
                                    COULEURS[nom], nom, 150), use_container_width=True)
        if not instantane:
            time.sleep(0.05)
    if t0 is None:
        st.success("Rejeu terminé : aucune dérive n'avait été injectée. Toute alerte est une fausse alerte.")
    else:
        st.info(f"Dérive injectée à t = {t0}. Comparez l'heure de la première alerte de chaque détecteur.")
else:
    st.info("Choisissez un scénario à gauche puis cliquez sur « Lancer la démo ».")