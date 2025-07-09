import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import List, Tuple

st.set_page_config(page_title="Couverture Température", page_icon="🧶", layout="wide")

if 'project_data' not in st.session_state:
    st.session_state.project_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'config'

PALETTE = {
    "colors": ["#08306B", "#2171B5", "#6BAED6", "#BDD7E7", "#FEE0D2", "#FC9272", "#DE2D26", "#A50F15"],
    "yarn_names": ["Bleu Foncé", "Bleu Moyen", "Bleu Clair", "Bleu Pâle", "Rose Clair", "Rose Moyen", "Rouge", "Rouge Foncé"]
}

def get_temperature_color(temp: float, palette: List[str], min_temp: float = -5, max_temp: float = 35) -> Tuple[str, str]:
    temp = max(min_temp, min(max_temp, temp))
    normalized = (temp - min_temp) / (max_temp - min_temp)
    index = int(normalized * (len(palette) - 1))
    return palette[index], PALETTE['yarn_names'][index]

def fetch_real_temperature_data(city: str, year: int) -> pd.DataFrame:
    coords = {
        "Paris": (48.8566, 2.3522),
        "Casablanca": (33.5731, -7.5898),
        "Londres": (51.5074, -0.1278),
        "Madrid": (40.4168, -3.7038),
        "Berlin": (52.5200, 13.4050)
    }
    lat, lon = coords.get(city, coords["Paris"])
    
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start}&end_date={end}"
        f"&daily=temperature_2m_max&timezone=auto"
    )
    
    r = requests.get(url)
    data = r.json()
    
    if "daily" not in data:
        st.error("Erreur de récupération des données météo.")
        return pd.DataFrame()
    
    dates = pd.to_datetime(data['daily']['time'])
    temps = data['daily']['temperature_2m_max']
    
    return pd.DataFrame({'date': dates, 'temperature': temps})

def page_config():
    st.title("🧶 Couverture Température avec données réelles")
    
    cities = ["Paris", "Casablanca", "Londres", "Madrid", "Berlin"]
    city = st.selectbox("Choisissez une ville :", cities)
    
    year = st.selectbox("Année :", list(range(2015, datetime.now().year + 1)), index=8)
    
    if st.button("🎉 Générer la couverture"):
        with st.spinner("Récupération des données météo..."):
            df = fetch_real_temperature_data(city, year)
            if not df.empty:
                st.session_state.project_data = {"city": city, "year": year, "data": df}
                st.session_state.current_page = 'project'
                st.rerun()

def page_project():
    data = st.session_state.project_data
    df = data['data']
    city = data['city']
    year = data['year']
    
    st.title(f"📆 Couverture : {city} - {year}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Jours de l'année", len(df))
    with col2:
        st.metric("Temp. Moyenne", f"{df['temperature'].mean():.1f}°C")
    
    st.markdown("### 🧵 Couleurs quotidiennes :")
    
    for month in range(1, 13):
        m_df = df[df['date'].dt.month == month]
        if m_df.empty:
            continue
        colors_html = ""
        for _, row in m_df.iterrows():
            color, _ = get_temperature_color(row['temperature'], PALETTE['colors'])
            colors_html += f'<span style="background-color:{color};width:10px;height:20px;display:inline-block;margin:1px;"></span>'
        month_name = datetime(2023, month, 1).strftime('%B')
        st.markdown(f"**{month_name}**")
        st.markdown(f'<div style="line-height:24px">{colors_html}</div>', unsafe_allow_html=True)

    if st.button("⬅️ Revenir à la configuration"):
        st.session_state.current_page = 'config'
        st.rerun()

def main():
    if st.session_state.current_page == 'config':
        page_config()
    else:
        page_project()

if __name__ == "__main__":
    main()
