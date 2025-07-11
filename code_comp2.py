import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

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

# --- LISTE ÉTENDUE DES VILLES ---
CITIES = {
    # Europe
    "Paris, France": (48.8566, 2.3522),
    "Lyon, France": (45.7640, 4.8357),
    "Marseille, France": (43.2965, 5.3698),
    "Toulouse, France": (43.6047, 1.4442),
    "Nice, France": (43.7102, 7.2620),
    "Nantes, France": (47.2184, -1.5536),
    "Strasbourg, France": (48.5734, 7.7521),
    "Montpellier, France": (43.6110, 3.8767),
    "Bordeaux, France": (44.8378, -0.5792),
    "Lille, France": (50.6292, 3.0573),
    
    "Londres, UK": (51.5074, -0.1278),
    "Manchester, UK": (53.4808, -2.2426),
    "Birmingham, UK": (52.4862, -1.8904),
    "Glasgow, UK": (55.8642, -4.2518),
    "Edinburgh, UK": (55.9533, -3.1883),
    "Liverpool, UK": (53.4084, -2.9916),
    "Cardiff, UK": (51.4816, -3.1791),
    "Belfast, UK": (54.5973, -5.9301),
    
    "Madrid, Spain": (40.4168, -3.7038),
    "Barcelone, Spain": (41.3851, 2.1734),
    "Valence, Spain": (39.4699, -0.3763),
    "Séville, Spain": (37.3891, -5.9845),
    "Saragosse, Spain": (41.6488, -0.8891),
    "Málaga, Spain": (36.7213, -4.4214),
    "Murcie, Spain": (37.9922, -1.1307),
    "Palma, Spain": (39.5696, 2.6502),
    "Las Palmas, Spain": (28.1248, -15.4300),
    "Bilbao, Spain": (43.2627, -2.9253),
    
    "Berlin, Germany": (52.5200, 13.4050),
    "Hambourg, Germany": (53.5511, 9.9937),
    "Munich, Germany": (48.1351, 11.5820),
    "Cologne, Germany": (50.9375, 6.9603),
    "Frankfurt, Germany": (50.1109, 8.6821),
    "Stuttgart, Germany": (48.7758, 9.1829),
    "Düsseldorf, Germany": (51.2277, 6.7735),
    "Dortmund, Germany": (51.5136, 7.4653),
    "Essen, Germany": (51.4556, 7.0116),
    "Leipzig, Germany": (51.3397, 12.3731),
    
    "Rome, Italy": (41.9028, 12.4964),
    "Milan, Italy": (45.4642, 9.1900),
    "Naples, Italy": (40.8518, 14.2681),
    "Turin, Italy": (45.0703, 7.6869),
    "Palerme, Italy": (38.1157, 13.3613),
    "Gênes, Italy": (44.4056, 8.9463),
    "Bologne, Italy": (44.4949, 11.3426),
    "Florence, Italy": (43.7696, 11.2558),
    "Bari, Italy": (41.1177, 16.8719),
    "Catane, Italy": (37.5079, 15.0830),
    
    "Amsterdam, Netherlands": (52.3676, 4.9041),
    "Rotterdam, Netherlands": (51.9244, 4.4777),
    "La Haye, Netherlands": (52.0705, 4.3007),
    "Utrecht, Netherlands": (52.0907, 5.1214),
    "Eindhoven, Netherlands": (51.4416, 5.4697),
    "Tilburg, Netherlands": (51.5555, 5.0913),
    "Groningen, Netherlands": (53.2194, 6.5665),
    "Almere, Netherlands": (52.3508, 5.2647),
    
    "Bruxelles, Belgium": (50.8503, 4.3517),
    "Anvers, Belgium": (51.2194, 4.4025),
    "Gand, Belgium": (51.0500, 3.7303),
    "Charleroi, Belgium": (50.4108, 4.4446),
    "Liège, Belgium": (50.6292, 5.5796),
    "Bruges, Belgium": (51.2093, 3.2247),
    "Namur, Belgium": (50.4669, 4.8674),
    "Louvain, Belgium": (50.8798, 4.7005),
    
    "Lisbonne, Portugal": (38.7223, -9.1393),
    "Porto, Portugal": (41.1579, -8.6291),
    "Braga, Portugal": (41.5518, -8.4229),
    "Coimbra, Portugal": (40.2033, -8.4103),
    "Funchal, Portugal": (32.6669, -16.9241),
    "Aveiro, Portugal": (40.6443, -8.6455),
    "Viseu, Portugal": (40.6566, -7.9122),
    "Leiria, Portugal": (39.7436, -8.8071),
    
    "Stockholm, Sweden": (59.3293, 18.0686),
    "Göteborg, Sweden": (57.7089, 11.9746),
    "Malmö, Sweden": (55.6044, 13.0038),
    "Uppsala, Sweden": (59.8586, 17.6389),
    "Västerås, Sweden": (59.6162, 16.5528),
    "Örebro, Sweden": (59.2753, 15.2134),
    "Linköping, Sweden": (58.4108, 15.6214),
    "Helsingborg, Sweden": (56.0465, 12.6945),
    
    "Oslo, Norway": (59.9139, 10.7522),
    "Bergen, Norway": (60.3913, 5.3221),
    "Stavanger, Norway": (58.9700, 5.7331),
    "Trondheim, Norway": (63.4305, 10.3951),
    "Drammen, Norway": (59.7439, 10.2045),
    "Fredrikstad, Norway": (59.2181, 10.9298),
    "Kristiansand, Norway": (58.1467, 7.9956),
    "Sandnes, Norway": (58.8516, 5.7369),
    
    "Copenhague, Denmark": (55.6761, 12.5683),
    "Aarhus, Denmark": (56.1629, 10.2039),
    "Odense, Denmark": (55.4038, 10.4024),
    "Aalborg, Denmark": (57.0488, 9.9217),
    "Esbjerg, Denmark": (55.4761, 8.4602),
    "Randers, Denmark": (56.4607, 10.0369),
    "Kolding, Denmark": (55.4904, 9.4721),
    "Horsens, Denmark": (55.8607, 9.8503),
    
    "Helsinki, Finland": (60.1699, 24.9384),
    "Espoo, Finland": (60.2055, 24.6559),
    "Tampere, Finland": (61.4978, 23.7610),
    "Vantaa, Finland": (60.2934, 25.0378),
    "Oulu, Finland": (65.0121, 25.4651),
    "Turku, Finland": (60.4518, 22.2666),
    "Jyväskylä, Finland": (62.2426, 25.7473),
    "Lahti, Finland": (60.9827, 25.6612),
    
    "Zurich, Switzerland": (47.3769, 8.5417),
    "Genève, Switzerland": (46.2044, 6.1432),
    "Bâle, Switzerland": (47.5596, 7.5886),
    "Lausanne, Switzerland": (46.5197, 6.6323),
    "Berne, Switzerland": (46.9481, 7.4474),
    "Winterthour, Switzerland": (47.5022, 8.7386),
    "Lucerne, Switzerland": (47.0502, 8.3093),
    "Saint-Gall, Switzerland": (47.4245, 9.3767),
    
    "Vienne, Austria": (48.2082, 16.3738),
    "Graz, Austria": (47.0707, 15.4395),
    "Linz, Austria": (48.3064, 14.2861),
    "Salzburg, Austria": (47.8095, 13.0550),
    "Innsbruck, Austria": (47.2692, 11.4041),
    "Klagenfurt, Austria": (46.6347, 14.3079),
    "Villach, Austria": (46.6111, 13.8558),
    "Wels, Austria": (48.1597, 14.0308),
    
    "Prague, Czech Republic": (50.0755, 14.4378),
    "Brno, Czech Republic": (49.1951, 16.6068),
    "Ostrava, Czech Republic": (49.8209, 18.2625),
    "Plzen, Czech Republic": (49.7384, 13.3736),
    "Liberec, Czech Republic": (50.7663, 15.0543),
    "Olomouc, Czech Republic": (49.5938, 17.2509),
    "Budweis, Czech Republic": (48.9744, 14.4744),
    "Hradec Králové, Czech Republic": (50.2103, 15.8327),
    
    "Varsovie, Poland": (52.2297, 21.0122),
    "Cracovie, Poland": (50.0647, 19.9450),
    "Wrocław, Poland": (51.1079, 17.0385),
    "Poznań, Poland": (52.4064, 16.9252),
    "Gdańsk, Poland": (54.3520, 18.6466),
    "Szczecin, Poland": (53.4285, 14.5528),
    "Bydgoszcz, Poland": (53.1235, 18.0084),
    "Lublin, Poland": (51.2465, 22.5684),
    
    "Budapest, Hungary": (47.4979, 19.0402),
    "Debrecen, Hungary": (47.5316, 21.6273),
    "Szeged, Hungary": (46.2530, 20.1414),
    "Miskolc, Hungary": (48.1034, 20.7784),
    "Pécs, Hungary": (46.0727, 18.2330),
    "Győr, Hungary": (47.6875, 17.6504),
    "Nyíregyháza, Hungary": (47.9556, 21.7267),
    "Kecskemét, Hungary": (46.9077, 19.6856),
    
    "Bucarest, Romania": (44.4268, 26.1025),
    "Cluj-Napoca, Romania": (46.7712, 23.6236),
    "Timișoara, Romania": (45.7489, 21.2087),
    "Iași, Romania": (47.1585, 27.6014),
    "Constanța, Romania": (44.1598, 28.6348),
    "Craiova, Romania": (44.3302, 23.7949),
    "Brașov, Romania": (45.6427, 25.5887),
    "Galați, Romania": (45.4353, 28.0080),
    
    "Sofia, Bulgaria": (42.6977, 23.3219),
    "Plovdiv, Bulgaria": (42.1354, 24.7453),
    "Varna, Bulgaria": (43.2141, 27.9147),
    "Burgas, Bulgaria": (42.5048, 27.4626),
    "Ruse, Bulgaria": (43.8564, 25.9560),
    "Stara Zagora, Bulgaria": (42.4354, 25.6397),
    "Pleven, Bulgaria": (43.4092, 24.6118),
    "Sliven, Bulgaria": (42.6824, 26.3150),
    
    "Zagreb, Croatia": (45.8150, 15.9819),
    "Split, Croatia": (43.5081, 16.4402),
    "Rijeka, Croatia": (45.3271, 14.4422),
    "Osijek, Croatia": (45.5550, 18.6955),
    "Zadar, Croatia": (44.1194, 15.2314),
    "Pula, Croatia": (44.8666, 13.8496),
    "Slavonski Brod, Croatia": (45.1600, 18.0158),
    "Karlovac, Croatia": (45.4870, 15.5378),
    
    "Ljubljana, Slovenia": (46.0569, 14.5058),
    "Maribor, Slovenia": (46.5547, 15.6459),
    "Celje, Slovenia": (46.2311, 15.2683),
    "Kranj, Slovenia": (46.2437, 14.3557),
    "Velenje, Slovenia": (46.3592, 15.1115),
    "Koper, Slovenia": (45.5469, 13.7294),
    "Novo Mesto, Slovenia": (45.8058, 15.1695),
    "Ptuj, Slovenia": (46.4214, 15.8704),
    
    "Bratislava, Slovakia": (48.1486, 17.1077),
    "Košice, Slovakia": (48.7164, 21.2611),
    "Prešov, Slovakia": (49.0014, 21.2393),
    "Žilina, Slovakia": (49.2237, 18.7398),
    "Banská Bystrica, Slovakia": (48.7362, 19.1532),
    "Nitra, Slovakia": (48.3081, 18.0972),
    "Trnava, Slovakia": (48.3774, 17.5877),
    "Martin, Slovakia": (49.0664, 18.9215),
    
    "Moscou, Russia": (55.7558, 37.6173),
    "Saint-Pétersbourg, Russia": (59.9311, 30.3609),
    "Novossibirsk, Russia": (55.0084, 82.9357),
    "Ekaterinbourg, Russia": (56.8431, 60.6454),
    "Nizhny Novgorod, Russia": (56.2965, 43.9361),
    "Kazan, Russia": (55.8304, 49.0661),
    "Tcheliabinsk, Russia": (55.1644, 61.4368),
    "Omsk, Russia": (54.9884, 73.3242),
    "Samara, Russia": (53.2001, 50.1500),
    "Rostov-sur-le-Don, Russia": (47.2357, 39.7015),
    
    "Kiev, Ukraine": (50.4501, 30.5234),
    "Kharkiv, Ukraine": (49.9935, 36.2304),
    "Odessa, Ukraine": (46.4825, 30.7233),
    "Dnipro, Ukraine": (48.4647, 35.0462),
    "Donetsk, Ukraine": (48.0159, 37.8029),
    "Zaporijjia, Ukraine": (47.8388, 35.1396),
    "Lviv, Ukraine": (49.8397, 24.0297),
    "Kryvyï Rih, Ukraine": (47.9077, 33.3917),
    
    "Minsk, Belarus": (53.9006, 27.5590),
    "Gomel, Belarus": (52.4345, 31.0136),
    "Moguilev, Belarus": (53.9168, 30.3449),
    "Vitebsk, Belarus": (55.1904, 30.2049),
    "Grodno, Belarus": (53.6884, 23.8258),
    "Brest, Belarus": (52.0975, 23.7340),
    "Babrouïsk, Belarus": (53.1384, 29.2214),
    "Baranovitchi, Belarus": (53.1327, 26.0139),
    
    "Athènes, Greece": (37.9838, 23.7275),
    "Thessalonique, Greece": (40.6401, 22.9444),
    "Patras, Greece": (38.2466, 21.7346),
    "Héraklion, Greece": (35.3387, 25.1442),
    "Larissa, Greece": (39.6390, 22.4194),
    "Volos, Greece": (39.3681, 22.9426),
    "Ioannina, Greece": (39.6650, 20.8537),
    "Kavala, Greece": (40.9396, 24.4019),
    
    "Belgrade, Serbia": (44.7866, 20.4489),
    "Novi Sad, Serbia": (45.2671, 19.8335),
    "Niš, Serbia": (43.3209, 21.8958),
    "Kragujevac, Serbia": (44.0165, 20.9114),
    "Subotica, Serbia": (46.1008, 19.6677),
    "Novi Pazar, Serbia": (43.1369, 20.5117),
    "Zrenjanin, Serbia": (45.3797, 20.3937),
    "Pančevo, Serbia": (44.8704, 20.6407),
    
    "Sarajevo, Bosnia and Herzegovina": (43.8563, 18.4131),
    "Banja Luka, Bosnia and Herzegovina": (44.7722, 17.1910),
    "Tuzla, Bosnia and Herzegovina": (44.5386, 18.6739),
    "Zenica, Bosnia and Herzegovina": (44.2039, 17.9060),
    "Mostar, Bosnia and Herzegovina": (43.3438, 17.8078),
    "Bijeljina, Bosnia and Herzegovina": (44.7594, 19.2144),
    "Brčko, Bosnia and Herzegovina": (44.8694, 18.8081),
    "Prijedor, Bosnia and Herzegovina": (44.9799, 16.7081),
    
    "Podgorica, Montenegro": (42.4304, 19.2594),
    "Nikšić, Montenegro": (42.7731, 18.9483),
    "Pljevlja, Montenegro": (43.3569, 19.3581),
    "Bijelo Polje, Montenegro": (43.0355, 19.7466),
    "Cetinje, Montenegro": (42.3911, 18.9238),
    "Bar, Montenegro": (42.0947, 19.0904),
    "Herceg Novi, Montenegro": (42.4511, 18.5370),
    "Berane, Montenegro": (42.8444, 19.8708),
    
    "Skopje, North Macedonia": (41.9973, 21.4280),
    "Bitola, North Macedonia": (41.0314, 21.3347),
    "Kumanovo, North Macedonia": (42.1322, 21.7144),
    "Prilep, North Macedonia": (41.3447, 21.5542),
    "Tetovo, North Macedonia": (42.0106, 20.9719),
    "Veles, North Macedonia": (41.7172, 21.7758),
    "Štip, North Macedonia": (41.7414, 22.1958),
    "Ohrid, North Macedonia": (41.1172, 20.8019),
    
    "Tirana, Albania": (41.3275, 19.8187),
    "Durrës, Albania": (41.3245, 19.4565),
    "Vlorë, Albania": (40.4686, 19.4914),
    "Shkodër, Albania": (42.0682, 19.5126),
    "Fier, Albania": (40.7239, 19.5550),
    "Korçë, Albania": (40.6086, 20.7728),
    "Berat, Albania": (40.7058, 19.9447),
    "Lushnjë, Albania": (40.9447, 19.7058),
    
    "Pristina, Kosovo": (42.6629, 21.1655),
    "Prizren, Kosovo": (42.2139, 20.7397),
    "Gjilan, Kosovo": (42.4633, 21.4694),
    "Peja, Kosovo": (42.6589, 20.2881),
    "Gjakova, Kosovo": (42.3789, 20.4314),
    "Ferizaj, Kosovo": (42.3706, 21.1486),
    "Mitrovica, Kosovo": (42.8814, 20.8647),
    "Vushtrri, Kosovo": (42.8231, 20.9689),
    
    "Chisinau, Moldova": (47.0105, 28.8638),
    "Tiraspol, Moldova": (46.8403, 29.6433),
    "Bălți, Moldova": (47.7615, 27.9297),
    "Bender, Moldova": (46.8317, 29.4767),
    "Rîbnița, Moldova": (47.7667, 29.0014),
    "Cahul, Moldova": (45.9081, 28.1981),
    "Ungheni, Moldova": (47.2108, 27.7978),
    "Soroca, Moldova": (48.1581, 28.2925),
    
    "Riga, Latvia": (56.9496, 24.1052),
    "Daugavpils, Latvia": (55.8744, 26.5275),
    "Liepāja, Latvia": (56.5053, 21.0108),
    "Jelgava, Latvia": (56.6500, 23.7294),
    "Jūrmala, Latvia": (56.9681, 23.7719),
    "Ventspils, Latvia": (57.3947, 21.5644),
    "Rēzekne, Latvia": (56.5100, 27.3333),
    "Valmiera, Latvia": (57.5408, 25.4272),
    
    "Vilnius, Lithuania": (54.6872, 25.2797),
    "Kaunas, Lithuania": (54.8985, 23.9036),
    "Klaipėda, Lithuania": (55.7033, 21.1443),
    "Šiauliai, Lithuania": (55.9347, 23.3144),
    "Panevėžys, Lithuania": (55.7353, 24.3602),
    "Alytus, Lithuania": (54.3961, 24.0456),
    "Marijampolė, Lithuania": (54.5597, 23.3544),
    "Mažeikiai, Lithuania": (56.3089, 22.3386),
    
    "Tallinn, Estonia": (59.4370, 24.7536),
    "Tartu, Estonia": (58.3780, 26.7290),
    "Narva, Estonia": (59.3769, 28.1903),
    "Pärnu, Estonia": (58.3859, 24.4971),
    "Kohtla-Järve, Estonia": (59.4036, 27.2728),
    "Viljandi, Estonia": (58.3640, 25.5906),
    "Rakvere, Estonia": (59.3469, 26.3553),
    "Kuressaare, Estonia": (58.2530, 22.4894),
    
    "Reykjavik, Iceland": (64.1466, -21.9426),
    "Akureyri, Iceland": (65.6835, -18.1262),
    "Hafnarfjörður, Iceland": (64.0671, -21.9556),
    "Keflavík, Iceland": (64.0049, -22.5636),
    "Akranes, Iceland": (64.3213, -22.0777),
    "Garðabær, Iceland": (64.0881, -21.9286),
    "Mosfellsbær, Iceland": (64.1677, -21.6894),
    "Selfoss, Iceland": (63.9336, -20.9975),
    
    "Dublin, Ireland": (53.3498, -6.2603),
    "Cork, Ireland": (51.8985, -8.4756),
    "Limerick, Ireland": (52.6638, -8.6267),
    "Galway, Ireland": (53.2707, -9.0568),
    "Waterford, Ireland": (52.2593, -7.1101),
    "Drogheda, Ireland": (53.7189, -6.3478),
    "Swords, Ireland": (53.4597, -6.2179),
    "Dundalk, Ireland": (54.0014, -6.4058)
}

def get_color_for_temperature(temp: float, palette_colors: List[str], min_temp: float = -20, max_temp: float = 40) -> Tuple[str, str]:
    """
    Retourne la couleur et le nom de la laine correspondant à la température
    """
    # Normaliser la température entre 0 et 1
    normalized_temp = max(0, min(1, (temp - min_temp) / (max_temp - min_temp)))
    
    # Calculer l'index dans la palette
    index = int(normalized_temp * (len(palette_colors) - 1))
    
    palette_name = st.session_state.get('selected_palette', 'Automne Classique')
    return palette_colors[index], PALETTES_COUVERTURE[palette_name]['yarn_colors'][index]

# --- Fonction pour récupérer les données depuis l'API Open-Meteo ---
@st.cache_data(show_spinner=True)
def get_real_temperature_data(lat: float, lon: float, year: int, temp_type: str) -> pd.DataFrame:
    """
    Récupère les données de température réelles depuis l'API Open-Meteo
    """
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    # Mapping des types de température
    daily_param = {
        "min": "temperature_2m_min",
        "max": "temperature_2m_max",
        "moyenne": "temperature_2m_mean"
    }[temp_type]

    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
        f"&daily={daily_param}&timezone=auto"
    )

    try:
        st.info(f"Récupération des données pour {lat}, {lon} en {year}...")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            json_data = response.json()
            
            # Vérifier si les données sont présentes
            if "daily" in json_data and "time" in json_data["daily"] and daily_param in json_data["daily"]:
                df = pd.DataFrame({
                    "date": pd.to_datetime(json_data["daily"]["time"]),
                    "temperature": json_data["daily"][daily_param]
                })
                
                # Filtrer les valeurs nulles
                df = df.dropna()
                
                if not df.empty:
                    st.success(f"Données récupérées avec succès! {len(df)} jours de données.")
                    return df
                else:
                    st.warning("Données vides récupérées de l'API. Utilisation de données simulées.")
                    return generate_fallback_data(year, temp_type)
            else:
                st.warning("Structure de données inattendue de l'API. Utilisation de données simulées.")
                return generate_fallback_data(year, temp_type)
        else:
            st.error(f"Erreur API: {response.status_code}. Utilisation de données simulées.")
            return generate_fallback_data(year, temp_type)
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Erreur réseau: {e}. Utilisation de données simulées.")
        return generate_fallback_data(year, temp_type)
    except Exception as e:
        st.error(f"Erreur inattendue: {e}. Utilisation de données simulées.")
        return generate_fallback_data(year, temp_type)

def generate_fallback_data(year: int, temp_type: str) -> pd.DataFrame:
    """
    Génère des données de température simulées en cas d'échec de l'API
    """
    st.info("Génération de données de température simulées...")
    
    # Températures de base par saison (approximatives pour l'Europe)
    base_temps = {
        "winter": 2,
        "spring": 12,
        "summer": 22,
        "autumn": 15
    }
    
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
        np.random.seed(current_date.timetuple().tm_yday + year)  # Reproductibilité
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
    
    df = pd.DataFrame({
        'date': dates,
        'temperature': temperatures
    })
    
    st.success(f"Données simulées générées avec succès! {len(df)} jours de données.")
    return df

def generate_temperature_data(city: str, year: int, temp_type: str) -> pd.DataFrame:
    """
    Récupère les données réelles de température pour une ville donnée
    """
    if city not in CITIES:
        st.error(f"Ville '{city}' non prise en charge.")
        return pd.DataFrame(columns=["date", "temperature"])
    
    lat, lon = CITIES[city]
    st.info(f"Récupération des données pour {city} ({lat}, {lon})")
    
    # Essayer d'abord avec l'API réelle
    df = get_real_temperature_data(lat, lon, year, temp_type)
    
    # Si les données sont vides, utiliser le fallback
    if df.empty:
        st.warning("Données API vides, génération de données simulées...")
        df = generate_fallback_data(year, temp_type)
    
    return df

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
        
        # Liste des villes avec les noms complets
        cities = list(CITIES.keys())
        
        selected_city = st.selectbox("Choisir une ville:", cities)
        
        # Choix de l'année
        current_year = datetime.now().year
        years = list(range(2020, current_year + 1))
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
        
        # Affichage simple de la palette
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
            try:
                # Générer les données
                df = generate_temperature_data(selected_city, selected_year, temp_type)
                
                if df.empty:
                    st.error("Impossible de générer les données. Veuillez réessayer.")
                    return
                
                # Afficher un échantillon des données pour debug
                st.success(f"✅ Données générées avec succès! {len(df)} jours de données.")
                
                # Afficher les premières lignes pour vérification
                with st.expander("Aperçu des données générées"):
                    st.dataframe(df.head(10))
                    st.write(f"Température min: {df['temperature'].min():.1f}°C")
                    st.write(f"Température max: {df['temperature'].max():.1f}°C")
                    st.write(f"Température moyenne: {df['temperature'].mean():.1f}°C")
                
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
                
                # Attendre un peu avant de changer de page
                import time
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur lors de la génération: {str(e)}")
                st.info("Essayez de changer d'année ou de ville.")

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
    
    # Afficher le tableau par chunks
    rows_per_page = 30
    total_rows = len(data_for_table)
    
    if total_rows > rows_per_page:
        page_num = st.selectbox("Page:", range(1, (total_rows // rows_per_page) + 2))
        start_idx = (page_num - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)
        data_to_show = data_for_table[start_idx:end_idx]
        st.info(f"Affichage des lignes {start_idx + 1} à {end_idx} sur {total_rows}")
    else:
        data_to_show = data_for_table
    
    # En-tête du tableau
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 2, 1, 1])
    with col1:
        st.write("**Date**")
    with col2:
        st.write("**Jour**")
    with col3:
        st.write("**Temp**")
    with col4:
        st.write("**Couleur**")
    with col5:
        st.write("**Statut**")
    with col6:
        st.write("**Action**")
    
    st.markdown("---")
    
    # Lignes du tableau
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
                st.success("✅ Fait")
            else:
                st.info("⏳ À faire")
        with col6:
            # Bouton pour marquer comme terminé/non terminé
            if st.button("✅" if not row['Terminé'] else "🔄", key=f"toggle_{row['date_key']}", help="Marquer comme terminé/non terminé"):
                st.session_state.progress_data[row['date_key']] = not row['Terminé']
                st.rerun()
    
    # Statistiques de progression
    st.markdown("---")
    st.subheader("📈 Progression du projet")
    
    total_days_all = len(df)
    completed_days = len([key for key in st.session_state.progress_data.keys() if st.session_state.progress_data[key]])
    progress_percentage = (completed_days / total_days_all * 100) if total_days_all > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lignes terminées", completed_days)
    with col2:
        st.metric("Lignes restantes", total_days_all - completed_days)
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
        if st.button("📊 Préparer export", type="secondary"):
            # Créer les données pour l'export
            export_data = []
            for idx, row in df.iterrows():
                date = row['date']
                temp = row['temperature']
                color, yarn_name = get_color_for_temperature(temp, palette_info['colors'])
                date_str = date.strftime('%Y-%m-%d')
                is_completed = st.session_state.progress_data.get(date_str, False)
                
                export_data.append({
                    'Date': date.strftime('%d/%m/%Y'),
                    'Jour': date.strftime('%A'),
                    'Température': f"{temp:.1f}°C",
                    'Couleur_Laine': yarn_name,
                    'Terminé': 'Oui' if is_completed else 'Non'
                })
            
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"couverture_{project['city'].replace(', ', '_')}_{project['year']}.csv",
                mime="text/csv"
            )
    with col3:
        if st.button("🎨 Aperçu simple", type="secondary"):
            st.subheader("👀 Aperçu couleurs continues (un jour = une ligne)")
    
            # Copier et trier le DataFrame
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
            df_copy = df_copy.sort_values('date')
    
            # Construire la bande de couleurs
            colors_html = ""
            for _, row in df_copy.iterrows():
                color, _ = get_color_for_temperature(row['temperature'], palette_info['colors'])
    
                colors_html += f'''
                    <div style="
                        background-color: {color};
                        height: 5px;
                        width: 100%;
                        margin-bottom: 1px;
                        border-radius: 4px;">
                    </div>
                '''
    
            st.markdown(colors_html, unsafe_allow_html=True)
    
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
    
