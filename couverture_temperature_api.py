
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Couverture Température - Données Réelles",
    page_icon="🧶",
    layout="wide"
)

# --- LISTE DES VILLES ---
CITIES = {
    "Casablanca, Maroc": (33.5731, -7.5898),
    "Paris, France": (48.8566, 2.3522),
    "Tokyo, Japon": (35.6895, 139.6917),
    "New York, USA": (40.7128, -74.0060),
    "Berlin, Allemagne": (52.5200, 13.4050),
    "Sydney, Australie": (-33.8688, 151.2093)
}

# --- PALETTES SIMPLIFIÉES ---
PALETTE = {
    "palette": ["#1E88E5", "#43A047", "#FB8C00", "#E53935", "#8E24AA", "#FDD835", "#00ACC1", "#6D4C41"],
    "description": "Palette standard 8 couleurs"
}

# --- Fonction pour récupérer les données depuis l'API Open-Meteo ---
@st.cache_data(show_spinner=True)
def get_real_temperature_data(lat, lon, year, temp_type):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    daily = {
        "min": "temperature_2m_min",
        "max": "temperature_2m_max",
        "moyenne": "temperature_2m_mean"
    }[temp_type]

    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
        f"&daily={daily}&timezone=auto"
    )

    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        return pd.DataFrame({
            "date": pd.to_datetime(json_data["daily"]["time"]),
            "temperature": json_data["daily"][daily]
        })
    else:
        st.error("Erreur lors de la récupération des données météo.")
        return pd.DataFrame(columns=["date", "temperature"])

# --- Interface Utilisateur ---
st.title("🧶 Projet de Couverture Température (avec données réelles)")

# Choix des paramètres
city_name = st.selectbox("🌍 Choisir une ville :", list(CITIES.keys()))
year = st.selectbox("📅 Choisir l'année :", list(range(datetime.now().year - 5, datetime.now().year + 1)))
temp_type = st.selectbox("🌡️ Type de température :", ["min", "moyenne", "max"])
color_list = PALETTE["palette"]

# Obtenir coordonnées
lat, lon = CITIES[city_name]

# Lancer la récupération des données
if st.button("📈 Générer la couverture"):
    df = get_real_temperature_data(lat, lon, year, temp_type)

    if not df.empty:
        st.success(f"{len(df)} jours de température récupérés pour {city_name} ({year})")

        # Attribution de couleur
        min_temp = -10
        max_temp = 40
        df["color"] = df["temperature"].apply(lambda t: color_list[
            min(len(color_list)-1, max(0, int((t - min_temp) / (max_temp - min_temp) * len(color_list))))])

        # Affichage graphique
        st.subheader("🎨 Températures journalières et couleurs associées")
        fig = go.Figure(data=go.Scatter(
            x=df["date"],
            y=df["temperature"],
            mode='markers',
            marker=dict(color=df["color"], size=8),
            text=[f"{d.date()} : {t}°C" for d, t in zip(df["date"], df["temperature"])],
        ))
        fig.update_layout(title="Température quotidienne", xaxis_title="Date", yaxis_title="Température (°C)")
        st.plotly_chart(fig, use_container_width=True)

        # Aperçu tableau
        st.subheader("🧵 Aperçu couverture (température → couleur)")
        st.dataframe(df[["date", "temperature", "color"]].rename(columns={
            "date": "Date", "temperature": "Température (°C)", "color": "Couleur"
        }))
