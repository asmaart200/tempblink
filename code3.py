import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple

# Imports conditionnels pour éviter les erreurs
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    st.error("Plotly n'est pas installé. Veuillez installer avec: pip install plotly")
    PLOTLY_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.metrics import r2_score, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    st.error("Scikit-learn n'est pas installé. Veuillez installer avec: pip install scikit-learn")
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    st.error("Scipy n'est pas installé. Veuillez installer avec: pip install scipy")
    SCIPY_AVAILABLE = False


# Configuration de la page
st.set_page_config(
    page_title="Couverture Température - Crochet/Tricot",
    page_icon="🧶",
    layout="wide"
)

# Initialisation des variables de session
if 'project_data' not in st.session_state:
    st.session_state.project_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'config'
if 'progress_data' not in st.session_state:
    st.session_state.progress_data = {}

# Palettes de couleurs pour les projets de couverture
PALETTES_COUVERTURE = {
    "Automne Classique": {
        "colors": ["#2C3E50", "#34495E", "#7F8C8D", "#BDC3C7", "#F39C12", "#E67E22", "#D35400", "#C0392B"],
        "description": "Tons d'automne chaleureux",
        "yarn_colors": ["Bleu Marine", "Gris Anthracite", "Gris Clair", "Beige", "Orange", "Terracotta", "Rouille", "Bordeaux"]
    },
    "Océan Profond": {
        "colors": ["#1A237E", "#303F9F", "#3F51B5", "#5C6BC0", "#7986CB", "#9FA8DA", "#C5CAE9", "#E8EAF6"],
        "description": "Dégradé d'océan apaisant",
        "yarn_colors": ["Bleu Nuit", "Bleu Royal", "Bleu Cobalt", "Bleu Lavande", "Bleu Ciel", "Bleu Pâle", "Bleu Glacier", "Blanc Cassé"]
    },
    "Forêt Enchantée": {
        "colors": ["#1B5E20", "#2E7D32", "#388E3C", "#4CAF50", "#66BB6A", "#81C784", "#A5D6A7", "#C8E6C9"],
        "description": "Verts naturels de la forêt",
        "yarn_colors": ["Vert Sapin", "Vert Forêt", "Vert Mousse", "Vert Prairie", "Vert Tendre", "Vert Menthe", "Vert Amande", "Vert Pastel"]
    },
    "Coucher de Soleil": {
        "colors": ["#4A148C", "#7B1FA2", "#9C27B0", "#E91E63", "#FF5722", "#FF9800", "#FFC107", "#FFEB3B"],
        "description": "Couleurs chaudes du coucher de soleil",
        "yarn_colors": ["Violet Profond", "Violet", "Magenta", "Rose Fuchsia", "Rouge Corail", "Orange Vif", "Jaune Doré", "Jaune Citron"]
    },
    "Hiver Nordique": {
        "colors": ["#263238", "#37474F", "#455A64", "#546E7A", "#607D8B", "#78909C", "#90A4AE", "#B0BEC5"],
        "description": "Tons froids d'hiver",
        "yarn_colors": ["Gris Charbon", "Gris Ardoise", "Gris Acier", "Gris Bleu", "Gris Perle", "Gris Argent", "Gris Clair", "Blanc Neige"]
    },
    "Prairie Printanière": {
        "colors": ["#880E4F", "#AD1457", "#C2185B", "#E91E63", "#EC407A", "#F48FB1", "#F8BBD9", "#FCE4EC"],
        "description": "Roses tendres du printemps",
        "yarn_colors": ["Rose Bordeaux", "Rose Foncé", "Rose Cerise", "Rose Vif", "Rose Bonbon", "Rose Poudré", "Rose Pâle", "Rose Nacré"]
    }
}

def get_color_for_temperature(temp: float, palette_colors: List[str], min_temp: float = -20, max_temp: float = 40) -> Tuple[str, str]:
    """
    Retourne la couleur et le nom de la laine correspondant à la température
    """
    # Normaliser la température entre 0 et 1
    normalized_temp = max(0, min(1, (temp - min_temp) / (max_temp - min_temp)))
    
    # Calculer l'index dans la palette
    index = int(normalized_temp * (len(palette_colors) - 1))
    
    return palette_colors[index], PALETTES_COUVERTURE[st.session_state.get('selected_palette', 'Automne Classique')]['yarn_colors'][index]

def generate_temperature_data(city: str, year: int, temp_type: str) -> pd.DataFrame:
    """
    Génère des données de température simulées pour une ville et une année
    """
    # Données de base pour différentes villes
    city_base_temps = {
        "Paris": {"winter": 5, "spring": 15, "summer": 25, "autumn": 12},
        "Londres": {"winter": 4, "spring": 12, "summer": 20, "autumn": 10},
        "Madrid": {"winter": 8, "spring": 18, "summer": 30, "autumn": 15},
        "Berlin": {"winter": 2, "spring": 12, "summer": 22, "autumn": 8},
        "Rome": {"winter": 10, "spring": 18, "summer": 28, "autumn": 16},
        "Amsterdam": {"winter": 3, "spring": 11, "summer": 19, "autumn": 9},
        "Bruxelles": {"winter": 4, "spring": 13, "summer": 21, "autumn": 11},
        "Lisbonne": {"winter": 12, "spring": 18, "summer": 26, "autumn": 19},
        "Stockholm": {"winter": -2, "spring": 8, "summer": 18, "autumn": 6},
        "Moscou": {"winter": -8, "spring": 5, "summer": 20, "autumn": 3},
        "Casablanca": {"winter": 15, "spring": 20, "summer": 28, "autumn": 22},
        "Tunis": {"winter": 12, "spring": 18, "summer": 32, "autumn": 20},
        "Alger": {"winter": 13, "spring": 19, "summer": 30, "autumn": 21}
    }
    
    base_temps = city_base_temps.get(city, city_base_temps["Paris"])
    
    # Générer les données pour l'année
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    dates = []
    temperatures = []
    
    current_date = start_date
    while current_date <= end_date:
        # Déterminer la saison
        month = current_date.month
        if month in [12, 1, 2]:
            season_temp = base_temps["winter"]
        elif month in [3, 4, 5]:
            season_temp = base_temps["spring"]
        elif month in [6, 7, 8]:
            season_temp = base_temps["summer"]
        else:
            season_temp = base_temps["autumn"]
        
        # Ajouter de la variation
        daily_variation = np.random.normal(0, 3)
        seasonal_variation = np.sin((current_date.timetuple().tm_yday / 365) * 2 * np.pi) * 5
        
        if temp_type == "min":
            temp = season_temp + seasonal_variation + daily_variation - 5
        elif temp_type == "max":
            temp = season_temp + seasonal_variation + daily_variation + 5
        else:  # moyenne
            temp = season_temp + seasonal_variation + daily_variation
        
        dates.append(current_date)
        temperatures.append(round(temp, 1))
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame({
        'date': dates,
        'temperature': temperatures
    })

def page_configuration():
    """
    Page de configuration du projet
    """
    st.title("🧶 Créateur de Couverture Température")
    st.markdown("### Créez votre couverture unique basée sur les températures !")
    
    st.markdown("---")
    
    # Configuration en colonnes
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🏙️ Localisation")
        
        # Liste des villes
        cities = [
            "Paris", "Londres", "Madrid", "Berlin", "Rome", 
            "Amsterdam", "Bruxelles", "Lisbonne", "Stockholm", 
            "Moscou", "Casablanca", "Tunis", "Alger"
        ]
        
        selected_city = st.selectbox("Choisir une ville:", cities)
        
        # Choix de l'année
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))
        selected_year = st.selectbox("Choisir l'année:", years, index=len(years)-1)
        
        # Type de température
        temp_type = st.selectbox(
            "Type de température:", 
            ["min", "max", "moyenne"],
            format_func=lambda x: {"min": "Température minimale", "max": "Température maximale", "moyenne": "Température moyenne"}[x]
        )
    
    with col2:
        st.subheader("🎨 Palette de couleurs")
        
        # Sélection de la palette
        selected_palette = st.selectbox(
            "Choisir une palette:",
            list(PALETTES_COUVERTURE.keys()),
            format_func=lambda x: f"{x} - {PALETTES_COUVERTURE[x]['description']}"
        )
        
        # Aperçu de la palette
        st.write("**Aperçu de la palette:**")
        palette_info = PALETTES_COUVERTURE[selected_palette]
        
        # Créer l'affichage de la palette
        for i, (color, yarn_name) in enumerate(zip(palette_info['colors'], palette_info['yarn_colors'])):
            temp_range = f"{-20 + i*7.5:.1f}°C à {-20 + (i+1)*7.5:.1f}°C"
            st.markdown(f"""
            <div style="
                background-color: {color};
                color: white;
                padding: 8px;
                margin: 2px 0;
                border-radius: 5px;
                font-size: 14px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            ">
                {yarn_name} - {temp_range}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bouton pour générer le projet
    if st.button("🚀 Générer mon projet de couverture", type="primary", use_container_width=True):
        with st.spinner("Génération des données de température..."):
            # Générer les données
            df = generate_temperature_data(selected_city, selected_year, temp_type)
            
            # Sauvegarder dans la session
            st.session_state.project_data = {
                'city': selected_city,
                'year': selected_year,
                'temp_type': temp_type,
                'palette': selected_palette,
                'data': df
            }
            st.session_state.selected_palette = selected_palette
            st.session_state.current_page = 'project'
            
            st.success("Projet généré avec succès!")
            st.rerun()

def page_project():
    """
    Page du projet avec le calendrier des couleurs
    """
    if st.session_state.project_data is None:
        st.error("Aucun projet généré. Retournez à la configuration.")
        if st.button("← Retour à la configuration"):
            st.session_state.current_page = 'config'
            st.rerun()
        return
    
    project = st.session_state.project_data
    df = project['data']
    palette_info = PALETTES_COUVERTURE[project['palette']]
    
    # En-tête du projet
    st.title(f"🧶 Couverture {project['city']} - {project['year']}")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("Ville", project['city'])
    with col2:
        st.metric("Année", project['year'])
    with col3:
        st.metric("Type", {"min": "Temp. Min", "max": "Temp. Max", "moyenne": "Temp. Moyenne"}[project['temp_type']])
    
    # Bouton retour
    if st.button("← Retour à la configuration"):
        st.session_state.current_page = 'config'
        st.rerun()
    
    st.markdown("---")
    
    # Statistiques du projet
    st.subheader("📊 Statistiques du projet")
    
    total_days = len(df)
    temp_min = df['temperature'].min()
    temp_max = df['temperature'].max()
    temp_avg = df['temperature'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Jours totaux", total_days)
    with col2:
        st.metric("Temp. Min", f"{temp_min:.1f}°C")
    with col3:
        st.metric("Temp. Max", f"{temp_max:.1f}°C")
    with col4:
        st.metric("Temp. Moyenne", f"{temp_avg:.1f}°C")
    
    # Graphique de température
    st.subheader("📈 Évolution des températures")
    
    fig = go.Figure()
    
    colors = []
    for temp in df['temperature']:
        color, _ = get_color_for_temperature(temp, palette_info['colors'])
        colors.append(color)
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['temperature'],
        mode='markers',
        marker=dict(
            color=colors,
            size=6,
            line=dict(width=1, color='white')
        ),
        name='Température'
    ))
    
    fig.update_layout(
        title=f"Températures {project['year']} - {project['city']}",
        xaxis_title="Date",
        yaxis_title="Température (°C)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Calendrier des couleurs avec suivi
    st.subheader("🗓️ Calendrier de crochet - Suivi des lignes")
    
    # Filtres
    col1, col2 = st.columns([1, 1])
    with col1:
        months = ['Tous'] + [f"{i:02d} - {datetime(2000, i, 1).strftime('%B')}" for i in range(1, 13)]
        selected_month = st.selectbox("Filtrer par mois:", months)
    
    with col2:
        show_completed = st.checkbox("Afficher seulement les lignes terminées")
    
    # Filtrer les données
    df_filtered = df.copy()
    if selected_month != 'Tous':
        month_num = int(selected_month.split(' - ')[0])
        df_filtered = df_filtered[df_filtered['date'].dt.month == month_num]
    
    # Créer le tableau de suivi
    st.subheader("📋 Tableau de suivi")
    
    # Créer les colonnes du tableau
    data_for_table = []
    
    for idx, row in df_filtered.iterrows():
        date = row['date']
        temp = row['temperature']
        color, yarn_name = get_color_for_temperature(temp, palette_info['colors'])
        
        # Vérifier si cette ligne est marquée comme terminée
        date_str = date.strftime('%Y-%m-%d')
        is_completed = st.session_state.progress_data.get(date_str, False)
        
        data_for_table.append({
            'Date': date.strftime('%d/%m/%Y'),
            'Jour': date.strftime('%A'),
            'Température': f"{temp:.1f}°C",
            'Couleur': yarn_name,
            'Terminé': is_completed,
            'date_key': date_str,
            'color_hex': color
        })
    
    # Filtrer selon le statut si nécessaire
    if show_completed:
        data_for_table = [row for row in data_for_table if row['Terminé']]
    
    # Afficher le tableau par chunks pour éviter les problèmes de performance
    rows_per_page = 50
    total_rows = len(data_for_table)
    
    if total_rows > rows_per_page:
        page_num = st.selectbox("Page:", range(1, (total_rows // rows_per_page) + 2))
        start_idx = (page_num - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)
        data_to_show = data_for_table[start_idx:end_idx]
    else:
        data_to_show = data_for_table
    
    # Créer le tableau interactif
    for i, row in enumerate(data_to_show):
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 2, 1, 1])
        
        with col1:
            st.write(row['Date'])
        with col2:
            st.write(row['Jour'])
        with col3:
            st.write(row['Température'])
        with col4:
            st.markdown(f"""
            <div style="
                background-color: {row['color_hex']};
                color: white;
                padding: 5px;
                border-radius: 3px;
                text-align: center;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            ">
                {row['Couleur']}
            </div>
            """, unsafe_allow_html=True)
        with col5:
            if row['Terminé']:
                st.success("✅")
            else:
                st.write("⏳")
        with col6:
            # Bouton pour marquer comme terminé/non terminé
            if st.button("✅" if not row['Terminé'] else "↩️", key=f"toggle_{row['date_key']}", help="Marquer comme terminé/non terminé"):
                st.session_state.progress_data[row['date_key']] = not row['Terminé']
                st.rerun()
    
    # Statistiques de progression
    st.markdown("---")
    st.subheader("📈 Progression du projet")
    
    total_days_filtered = len(data_for_table)
    completed_days = len([row for row in data_for_table if row['Terminé']])
    progress_percentage = (completed_days / total_days_filtered * 100) if total_days_filtered > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lignes terminées", completed_days)
    with col2:
        st.metric("Lignes restantes", total_days_filtered - completed_days)
    with col3:
        st.metric("Progression", f"{progress_percentage:.1f}%")
    
    # Barre de progression
    st.progress(progress_percentage / 100)
    
    # Boutons d'action
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Réinitialiser progression", type="secondary"):
            st.session_state.progress_data = {}
            st.success("Progression réinitialisée!")
            st.rerun()
    
    with col2:
        if st.button("📊 Exporter données", type="secondary"):
            # Créer un DataFrame pour l'export
            export_data = []
            for row in data_for_table:
                export_data.append({
                    'Date': row['Date'],
                    'Jour': row['Jour'],
                    'Température': row['Température'],
                    'Couleur_Laine': row['Couleur'],
                    'Terminé': 'Oui' if row['Terminé'] else 'Non'
                })
            
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"couverture_{project['city']}_{project['year']}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🎨 Aperçu couverture", type="secondary"):
            # Créer un aperçu visuel de la couverture
            st.subheader("👀 Aperçu de votre couverture")
            
            # Créer une grille de couleurs
            colors_grid = []
            for row in data_for_table:
                colors_grid.append(row['color_hex'])
            
            # Organiser en grille (par exemple, 10 colonnes)
            cols = 10
            rows = len(colors_grid) // cols + (1 if len(colors_grid) % cols != 0 else 0)
            
            fig_grid = go.Figure()
            
            for i, color in enumerate(colors_grid):
                row = i // cols
                col = i % cols
                
                fig_grid.add_trace(go.Scatter(
                    x=[col],
                    y=[rows - row],
                    mode='markers',
                    marker=dict(
                        color=color,
                        size=15,
                        symbol='square'
                    ),
                    showlegend=False,
                    hovertemplate=f"Jour {i+1}<br>Couleur: {data_for_table[i]['Couleur']}<br>Temp: {data_for_table[i]['Température']}<extra></extra>"
                ))
            
            fig_grid.update_layout(
                title="Aperçu de votre couverture température",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_grid, use_container_width=True)

# Interface principale
def main():
    # Sidebar avec informations
    st.sidebar.title("🧶 Couverture Température")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("""
    ### 📋 Instructions
    
    1. **Configuration**: Choisissez votre ville, année, type de température et palette
    2. **Génération**: Créez votre projet personnalisé
    3. **Suivi**: Cochez les lignes terminées au fur et à mesure
    4. **Export**: Téléchargez vos données
    
    ### 🎯 Principe
    - Chaque jour = 1 ligne de crochet
    - Couleur basée sur la température
    - Suivi de progression intégré
    
    ### 🧶 Conseils
    - Utilisez une laine de même épaisseur
    - Gardez vos pelotes organisées
    - Crochetez régulièrement !
    """)
    
    # Navigation
    if st.session_state.current_page == 'config':
        page_configuration()
    elif st.session_state.current_page == 'project':
        page_project()

if __name__ == "__main__":
    main()