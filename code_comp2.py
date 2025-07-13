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

    # Asie
    "Tokyo, Japan": (35.6762, 139.6503),
    "Yokohama, Japan": (35.4437, 139.6380),
    "Osaka, Japan": (34.6937, 135.5023),
    "Nagoya, Japan": (35.1815, 136.9066),
    "Sapporo, Japan": (43.0642, 141.3469),
    "Kobe, Japan": (34.6901, 135.1956),
    "Kyoto, Japan": (35.0116, 135.7681),
    "Fukuoka, Japan": (33.5904, 130.4017),
    "Hiroshima, Japan": (34.3853, 132.4553),
    "Sendai, Japan": (38.2682, 140.8694),
    
    "Beijing, China": (39.9042, 116.4074),
    "Shanghai, China": (31.2304, 121.4737),
    "Guangzhou, China": (23.1291, 113.2644),
    "Shenzhen, China": (22.5431, 114.0579),
    "Chongqing, China": (29.5630, 106.5516),
    "Tianjin, China": (39.3434, 117.3616),
    "Chengdu, China": (30.5728, 104.0668),
    "Wuhan, China": (30.5928, 114.305),
    "Dongguan, China": (23.0489, 113.7447),
    "Xi'an, China": (34.3416, 108.9398),
    "Hangzhou, China": (30.2741, 120.1551),
    "Foshan, China": (23.0218, 113.1219),
    "Nanjing, China": (32.0603, 118.7969),
    "Shenyang, China": (41.8057, 123.4315),
    "Harbin, China": (45.8038, 126.5349),
    
    "Mumbai, India": (19.0760, 72.8777),
    "Delhi, India": (28.7041, 77.1025),
    "Bangalore, India": (12.9716, 77.5946),
    "Hyderabad, India": (17.3850, 78.4867),
    "Ahmedabad, India": (23.0225, 72.5714),
    "Chennai, India": (13.0827, 80.2707),
    "Kolkata, India": (22.5726, 88.3639),
    "Pune, India": (18.5204, 73.8567),
    "Jaipur, India": (26.9124, 75.7873),
    "Surat, India": (21.1702, 72.8311),
    "Lucknow, India": (26.8467, 80.9462),
    "Kanpur, India": (26.4499, 80.3319),
    "Nagpur, India": (21.1458, 79.0882),
    "Indore, India": (22.7196, 75.8577),
    "Bhopal, India": (23.2599, 77.4126),
    
    "Séoul, South Korea": (37.5665, 126.9780),
    "Busan, South Korea": (35.1796, 129.0756),
    "Incheon, South Korea": (37.4563, 126.7052),
    "Daegu, South Korea": (35.8722, 128.6014),
    "Daejeon, South Korea": (36.3504, 127.3845),
    "Gwangju, South Korea": (35.1595, 126.8526),
    "Ulsan, South Korea": (35.5384, 129.3114),
    "Suwon, South Korea": (37.2636, 127.0286),
    
    "Bangkok, Thailand": (13.7563, 100.5018),
    "Nonthaburi, Thailand": (13.8621, 100.5144),
    "Nakhon Ratchasima, Thailand": (14.9799, 102.0977),
    "Chiang Mai, Thailand": (18.7883, 98.9853),
    "Hat Yai, Thailand": (7.0067, 100.4681),
    "Udon Thani, Thailand": (17.4138, 102.7875),
    "Pak Kret, Thailand": (13.9095, 100.5033),
    "Khon Kaen, Thailand": (16.4322, 102.8236),
    
    "Hô Chi Minh-Ville, Vietnam": (10.8231, 106.6297),
    "Hanoi, Vietnam": (21.0285, 105.8542),
    "Haiphong, Vietnam": (20.8449, 106.6881),
    "Da Nang, Vietnam": (16.0544, 108.2022),
    "Bien Hoa, Vietnam": (10.9571, 106.8197),
    "Hue, Vietnam": (16.4637, 107.5909),
    "Nha Trang, Vietnam": (12.2388, 109.1967),
    "Can Tho, Vietnam": (10.0452, 105.7469),
    
    "Jakarta, Indonesia": (6.2088, 106.8456),
    "Surabaya, Indonesia": (7.2575, 112.7521),
    "Bandung, Indonesia": (6.9175, 107.6191),
    "Bekasi, Indonesia": (6.2383, 106.9756),
    "Medan, Indonesia": (3.5952, 98.6722),
    "Tangerang, Indonesia": (6.1783, 106.6319),
    "Depok, Indonesia": (6.4025, 106.7942),
    "Semarang, Indonesia": (6.9667, 110.4167),
    "Palembang, Indonesia": (2.9761, 104.7754),
    "Makassar, Indonesia": (5.1477, 119.4327),
    
    "Manille, Philippines": (14.5995, 120.9842),
    "Quezon City, Philippines": (14.6760, 121.0437),
    "Davao, Philippines": (7.1907, 125.4553),
    "Caloocan, Philippines": (14.6507, 120.9668),
    "Cebu City, Philippines": (10.3157, 123.8854),
    "Zamboanga, Philippines": (6.9214, 122.0790),
    "Antipolo, Philippines": (14.5932, 121.1735),
    "Taguig, Philippines": (14.5176, 121.0509),
    
    "Kuala Lumpur, Malaysia": (3.1390, 101.6869),
    "George Town, Malaysia": (5.4164, 100.3327),
    "Ipoh, Malaysia": (4.5975, 101.0901),
    "Shah Alam, Malaysia": (3.0733, 101.5185),
    "Petaling Jaya, Malaysia": (3.1073, 101.6067),
    "Johor Bahru, Malaysia": (1.4927, 103.7414),
    "Seremban, Malaysia": (2.7297, 101.9381),
    "Kuching, Malaysia": (1.5533, 110.3592),
    
    "Singapour, Singapore": (1.3521, 103.8198),
    
    "Pyongyang, North Korea": (39.0392, 125.7625),
    "Hamhung, North Korea": (39.9187, 127.5358),
    "Chongjin, North Korea": (41.7846, 129.7762),
    "Nampo, North Korea": (38.7378, 125.4072),
    "Wonsan, North Korea": (39.1667, 127.4333),
    "Sinuiju, North Korea": (40.1006, 124.3983),
    "Tanchon, North Korea": (40.4289, 128.9422),
    "Kaechon, North Korea": (39.6833, 125.9167),
    
    "Dhaka, Bangladesh": (23.8103, 90.4125),
    "Chittagong, Bangladesh": (22.3569, 91.7832),
    "Sylhet, Bangladesh": (24.8949, 91.8687),
    "Khulna, Bangladesh": (22.8456, 89.5403),
    "Rajshahi, Bangladesh": (24.3636, 88.6241),
    "Rangpur, Bangladesh": (25.7439, 89.2752),
    "Comilla, Bangladesh": (23.4607, 91.1809),
    "Barisal, Bangladesh": (22.7010, 90.3535),
    
    "Islamabad, Pakistan": (33.7294, 73.0931),
    "Karachi, Pakistan": (24.8607, 67.0011),
    "Lahore, Pakistan": (31.5804, 74.3587),
    "Faisalabad, Pakistan": (31.4504, 73.1350),
    "Rawalpindi, Pakistan": (33.5651, 73.0169),
    "Gujranwala, Pakistan": (32.1877, 74.1945),
    "Peshawar, Pakistan": (34.0151, 71.5249),
    "Multan, Pakistan": (30.1575, 71.5249),
    
    "Kaboul, Afghanistan": (34.5553, 69.2075),
    "Kandahar, Afghanistan": (31.6080, 65.7384),
    "Herat, Afghanistan": (34.3667, 62.2000),
    "Mazar-i-Sharif, Afghanistan": (36.7081, 67.1106),
    "Jalalabad, Afghanistan": (34.4415, 70.4492),
    "Kunduz, Afghanistan": (36.7289, 68.8579),
    "Lashkar Gah, Afghanistan": (31.5939, 64.3615),
    "Taloqan, Afghanistan": (36.7361, 69.5347),
    
    "Téhéran, Iran": (35.6892, 51.3890),
    "Mashhad, Iran": (36.2605, 59.6168),
    "Isfahan, Iran": (32.6546, 51.6746),
    "Karaj, Iran": (35.8327, 50.9916),
    "Shiraz, Iran": (29.5918, 52.5837),
    "Tabriz, Iran": (38.0962, 46.2738),
    "Qom, Iran": (34.6401, 50.8764),
    "Ahvaz, Iran": (31.3183, 48.6706),
    
    "Bagdad, Iraq": (33.3152, 44.3661),
    "Bassora, Iraq": (30.5085, 47.7804),
    "Mossoul, Iraq": (36.3350, 43.1189),
    "Erbil, Iraq": (36.1911, 44.0093),
    "Najaf, Iraq": (32.0003, 44.3292),
    "Karbala, Iraq": (32.6160, 44.0244),
    "Kirkouk, Iraq": (35.4681, 44.3922),
    "Souleïmaniye, Iraq": (35.5651, 45.4372),
    
    "Riyad, Saudi Arabia": (24.7136, 46.6753),
    "Djeddah, Saudi Arabia": (21.4858, 39.1925),
    "La Mecque, Saudi Arabia": (21.3891, 39.8579),
    "Médine, Saudi Arabia": (24.5247, 39.5692),
    "Dammam, Saudi Arabia": (26.3927, 49.9777),
    "Taif, Saudi Arabia": (21.2703, 40.4158),
    "Tabuk, Saudi Arabia": (28.3998, 36.5700),
    "Buraydah, Saudi Arabia": (26.3260, 43.9750),
    
    "Koweït City, Kuwait": (29.3759, 47.9774),
    "Ahmadi, Kuwait": (29.0769, 48.0838),
    "Hawalli, Kuwait": (29.3327, 48.0287),
    "As Salimiyah, Kuwait": (29.3336, 48.0757),
    "Jahra, Kuwait": (29.3375, 47.6581),
    "Farwaniya, Kuwait": (29.2775, 47.9586),
    "Abraq Khaitan, Kuwait": (29.2930, 47.9304),
    "Fintas, Kuwait": (29.1736, 48.1208),
    
    "Manama, Bahrain": (26.2285, 50.5860),
    "Riffa, Bahrain": (26.1300, 50.5550),
    "Muharraq, Bahrain": (26.2540, 50.6115),
    "Hamad Town, Bahrain": (26.1442, 50.5121),
    "A'ali, Bahrain": (26.1591, 50.5236),
    "Isa Town, Bahrain": (26.1738, 50.5479),
    "Sitra, Bahrain": (26.1519, 50.6266),
    "Budaiya, Bahrain": (26.2042, 50.4561),
    
    "Doha, Qatar": (25.2760, 51.5200),
    "Al Rayyan, Qatar": (25.2928, 51.4264),
    "Umm Salal, Qatar": (25.4058, 51.4064),
    "Al Wakrah, Qatar": (25.1654, 51.6042),
    "Al Khor, Qatar": (25.6814, 51.4969),
    "Dukhan, Qatar": (25.4242, 50.7811),
    "Lusail, Qatar": (25.3847, 51.5206),
    "Mesaieed, Qatar": (24.9889, 51.5536),
    
    "Abou Dhabi, UAE": (24.4539, 54.3773),
    "Dubai, UAE": (25.2048, 55.2708),
    "Charjah, UAE": (25.3463, 55.4209),
    "Al Ain, UAE": (24.2075, 55.7447),
    "Ajman, UAE": (25.4052, 55.5136),
    "Ras al-Khaimah, UAE": (25.7889, 35.9444),
    "Fujairah, UAE": (25.1164, 56.3473),
    "Umm al-Quwain, UAE": (25.5647, 55.6831),
    
    "Mascate, Oman": (23.5880, 58.3829),
    "Seeb, Oman": (23.6700, 58.1900),
    "Salalah, Oman": (17.0151, 54.0924),
    "Bawshar, Oman": (23.5774, 58.3988),
    "Sohar, Oman": (24.3477, 56.7085),
    "As Suwayq, Oman": (23.8493, 57.4386),
    "Ibri, Oman": (23.2257, 56.5157),
    "Saham, Oman": (24.1667, 56.8833),
    
    "Sanaa, Yemen": (15.3694, 44.1910),
    "Aden, Yemen": (12.7797, 45.0369),
    "Taizz, Yemen": (13.6019, 44.0219),
    "Hodeidah, Yemen": (14.7978, 42.9545),
    "Ibb, Yemen": (13.9667, 44.1833),
    "Dhamar, Yemen": (14.5426, 44.4054),
    "Mukalla, Yemen": (14.5425, 49.1242),
    "Hajjah, Yemen": (15.6947, 43.6042),
    
    "Amman, Jordan": (31.9454, 35.9284),
    "Zarqa, Jordan": (32.0728, 36.0876),
    "Irbid, Jordan": (32.5556, 35.8500),
    "Russeifa, Jordan": (32.0177, 36.0465),
    "Wadi as-Sir, Jordan": (31.9539, 35.8186),
    "Aqaba, Jordan": (29.5320, 35.0063),
    "Madaba, Jordan": (31.7197, 35.7956),
    "As-Salt, Jordan": (32.0389, 35.7281),
    
    "Beyrouth, Lebanon": (33.8938, 35.5018),
    "Tripoli, Lebanon": (34.4444, 35.8497),
    "Sidon, Lebanon": (33.5633, 35.3689),
    "Tyre, Lebanon": (33.2704, 35.2038),
    "Nabatiye, Lebanon": (33.3789, 35.4839),
    "Jounieh, Lebanon": (33.9833, 35.6167),
    "Zahle, Lebanon": (33.8472, 35.9019),
    "Baalbek, Lebanon": (34.0059, 36.2039),
    
    "Damas, Syria": (33.5138, 36.2765),
    "Alep, Syria": (36.2021, 37.1343),
    "Homs, Syria": (34.7394, 36.7134),
    "Hamah, Syria": (35.1324, 36.7581),
    "Lattaquié, Syria": (35.5211, 35.7851),
    "Deir ez-Zor, Syria": (35.3370, 40.1467),
    "Tartous, Syria": (34.8833, 35.8833),
    "Idlib, Syria": (35.9333, 36.6333),
    
    "Ankara, Turkey": (39.9334, 32.8597),
    "Istanbul, Turkey": (41.0082, 28.9784),
    "Izmir, Turkey": (38.4192, 27.1287),
    "Bursa, Turkey": (40.1826, 29.0665),
    "Adana, Turkey": (37.0000, 35.3213),
    "Gaziantep, Turkey": (37.0662, 37.3833),
    "Konya, Turkey": (37.8667, 32.4833),
    "Antalya, Turkey": (36.8969, 30.7133),
    
    "Bakou, Azerbaijan": (40.4093, 49.8671),
    "Ganja, Azerbaijan": (40.6828, 46.3606),
    "Sumqayit, Azerbaijan": (40.5892, 49.6681),
    "Mingachevir, Azerbaijan": (40.7697, 47.0594),
    "Quba, Azerbaijan": (41.3617, 48.5122),
    "Lankaran, Azerbaijan": (38.7542, 48.8508),
    "Shaki, Azerbaijan": (41.1919, 47.1706),
    "Yevlakh, Azerbaijan": (40.6181, 47.1500),
    
    "Erevan, Armenia": (40.1792, 44.4991),
    "Gyumri, Armenia": (40.7894, 43.8414),
    "Vanadzor, Armenia": (40.8058, 44.4939),
    "Vagharshapat, Armenia": (40.1561, 44.2894),
    "Hrazdan, Armenia": (40.4975, 44.7644),
    "Abovyan, Armenia": (40.2694, 44.6331),
    "Kapan, Armenia": (39.2067, 46.4061),
    "Armavir, Armenia": (40.1456, 43.9314),
    
    "Tbilissi, Georgia": (41.7151, 44.8271),
    "Kutaisi, Georgia": (42.2488, 42.7058),
    "Batumi, Georgia": (41.6168, 41.6367),
    "Soukhoumi, Georgia": (42.8694, 40.0792),
    "Zugdidi, Georgia": (42.5088, 41.8708),
    "Gori, Georgia": (41.9847, 44.1086),
    "Poti, Georgia": (42.1488, 41.6672),
    "Kobuleti, Georgia": (41.8167, 41.7833),

# Afrique
    "Le Caire, Egypt": (30.0444, 31.2357),
    "Alexandrie, Egypt": (31.2001, 29.9187),
    "Gizeh, Egypt": (30.0131, 31.2089),
    "Shubra El Kheima, Egypt": (30.1218, 31.2444),
    "Port-Saïd, Egypt": (31.2653, 32.3019),
    "Suez, Egypt": (29.9668, 32.5498),
    "Mansoura, Egypt": (31.0409, 31.3785),
    "Tanta, Egypt": (30.7865, 31.0004),
    "Asyut, Egypt": (27.1809, 31.1837),
    "Fayoum, Egypt": (29.3084, 30.8428),
    "Zagazig, Egypt": (30.5965, 31.5026),
    "Ismailia, Egypt": (30.5965, 32.2715),
    "Aswan, Egypt": (24.0889, 32.8998),
    "Luxor, Egypt": (25.6872, 32.6396),
    "Damanhur, Egypt": (31.0341, 30.4682),
    "Minya, Egypt": (28.0871, 30.7618),
    "Sohag, Egypt": (26.5569, 31.6948),
    "Qena, Egypt": (26.1551, 32.7160),
    "Beni Suef, Egypt": (29.0661, 31.0994),
    "Kafr el-Sheikh, Egypt": (31.1107, 30.9388),
    
    "Lagos, Nigeria": (6.5244, 3.3792),
    "Kano, Nigeria": (12.0022, 8.5920),
    "Ibadan, Nigeria": (7.3775, 3.9470),
    "Abuja, Nigeria": (9.0579, 7.4951),
    "Port Harcourt, Nigeria": (4.8156, 7.0498),
    "Benin City, Nigeria": (6.3350, 5.6037),
    "Maiduguri, Nigeria": (11.8311, 13.1610),
    "Zaria, Nigeria": (11.0666, 7.7336),
    "Aba, Nigeria": (5.1066, 7.3667),
    "Jos, Nigeria": (9.9285, 8.8921),
    "Ilorin, Nigeria": (8.4966, 4.5426),
    "Oyo, Nigeria": (7.8527, 3.9470),
    "Enugu, Nigeria": (6.5244, 7.5086),
    "Abeokuta, Nigeria": (7.1475, 3.3619),
    "Kaduna, Nigeria": (10.5222, 7.4383),
    "Akure, Nigeria": (7.2571, 5.2058),
    "Bauchi, Nigeria": (10.3158, 9.8442),
    "Sokoto, Nigeria": (13.0059, 5.2476),
    "Onitsha, Nigeria": (6.1666, 6.7833),
    "Warri, Nigeria": (5.5167, 5.7500),
    "Okene, Nigeria": (7.5492, 6.2350),
    "Calabar, Nigeria": (4.9517, 8.3220),
    "Uyo, Nigeria": (5.0104, 7.8569),
    "Gombe, Nigeria": (10.2958, 11.1667),
    "Katsina, Nigeria": (12.9908, 7.6006),
    "Minna, Nigeria": (9.6140, 6.5569),
    "Owerri, Nigeria": (5.4839, 7.0333),
    "Umuahia, Nigeria": (5.5255, 7.4951),
    "Ede, Nigeria": (7.7333, 4.4500),
    "Damaturu, Nigeria": (11.7479, 11.9609),
    
    "Casablanca, Morocco": (33.5731, -7.5898),
    "Rabat, Morocco": (34.0209, -6.8417),
    "Marrakech, Morocco": (31.6295, -7.9811),
    "Fès, Morocco": (34.0181, -5.0078),
    "Tanger, Morocco": (35.7595, -5.8340),
    "Salé, Morocco": (34.0531, -6.7985),
    "Meknès, Morocco": (33.8935, -5.5473),
    "Oujda, Morocco": (34.6814, -1.9086),
    "Kénitra, Morocco": (34.2610, -6.5802),
    "Tétouan, Morocco": (35.5889, -5.3626),
    "Safi, Morocco": (32.2994, -9.2372),
    "Mohammedia, Morocco": (33.6861, -7.3833),
    "Khouribga, Morocco": (32.8811, -6.9063),
    "El Jadida, Morocco": (33.2316, -8.5007),
    "Béni Mellal, Morocco": (32.3373, -6.3498),
    "Nador, Morocco": (35.1681, -2.9287),
    "Taza, Morocco": (34.2133, -4.0103),
    "Settat, Morocco": (33.0018, -7.6160),
    "Larache, Morocco": (35.1932, -6.1557),
    "Khemisset, Morocco": (33.8244, -6.0691),
    "Guelmim, Morocco": (28.9870, -10.0574),
    "Berrechid, Morocco": (33.2654, -7.5836),
    "Ksar El Kébir, Morocco": (35.0063, -5.9078),
    "Errachidia, Morocco": (31.9314, -4.4265),
    "Ouarzazate, Morocco": (30.9189, -6.8939),
    "Tiznit, Morocco": (29.6974, -9.7316),
    "Taroudant, Morocco": (30.4731, -8.8777),
    "Sefrou, Morocco": (33.8307, -4.8370),
    "Youssoufia, Morocco": (32.2465, -8.5305),
    "Tan-Tan, Morocco": (28.4378, -11.1033),
    
    "Alger, Algeria": (36.7538, 3.0588),
    "Oran, Algeria": (35.6969, -0.6331),
    "Constantine, Algeria": (36.3650, 6.6147),
    "Annaba, Algeria": (36.9000, 7.7667),
    "Batna, Algeria": (35.5559, 6.1740),
    "Djelfa, Algeria": (34.6792, 3.2630),
    "Sétif, Algeria": (36.1919, 5.4133),
    "Sidi Bel Abbès, Algeria": (35.1878, -0.6390),
    "Biskra, Algeria": (34.8518, 5.7280),
    "Tébessa, Algeria": (35.4017, 8.1241),
    "Blida, Algeria": (36.4203, 2.8277),
    "Tlemcen, Algeria": (34.8780, -1.3157),
    "Béjaïa, Algeria": (36.7525, 5.0844),
    "Tiaret, Algeria": (35.3671, 1.3170),
    "Bordj Bou Arreridj, Algeria": (36.0731, 4.7608),
    "Tizi Ouzou, Algeria": (36.7118, 4.0435),
    "Jijel, Algeria": (36.8190, 5.7667),
    "Skikda, Algeria": (36.8761, 6.9086),
    "Chlef, Algeria": (36.1653, 1.3302),
    "Médéa, Algeria": (36.2639, 2.7539),
    "Saida, Algeria": (34.8408, 0.1517),
    "Mascara, Algeria": (35.3962, 0.1406),
    "Ouargla, Algeria": (31.9539, 5.3176),
    "Ghardaïa, Algeria": (32.4840, 3.6791),
    "Laghouat, Algeria": (33.8007, 2.8648),
    "Khenchela, Algeria": (35.4361, 7.1434),
    "Oum El Bouaghi, Algeria": (35.8753, 7.1134),
    "Souk Ahras, Algeria": (36.2865, 7.9515),
    "Guelma, Algeria": (36.4617, 7.4283),
    "M'Sila, Algeria": (35.7017, 4.5412),
    
    "Tunis, Tunisia": (36.8065, 10.1815),
    "Sfax, Tunisia": (34.7406, 10.7603),
    "Sousse, Tunisia": (35.8256, 10.6369),
    "Ettadhamen, Tunisia": (36.8667, 10.1833),
    "Kairouan, Tunisia": (35.6781, 10.0963),
    "Gabès, Tunisia": (33.8815, 10.0982),
    "Bizerte, Tunisia": (37.2746, 9.8739),
    "Ariana, Tunisia": (36.8625, 10.1953),
    "Gafsa, Tunisia": (34.4250, 8.7842),
    "Monastir, Tunisia": (35.7643, 10.8113),
    "Ben Arous, Tunisia": (36.7544, 10.2176),
    "Kasserine, Tunisia": (35.1676, 8.8369),
    "Médenine, Tunisia": (33.3548, 10.5055),
    "Nabeul, Tunisia": (36.4560, 10.7376),
    "Tataouine, Tunisia": (32.9297, 10.4518),
    "Béja, Tunisia": (36.7256, 9.1816),
    "Jendouba, Tunisia": (36.5011, 8.7803),
    "Kef, Tunisia": (36.1743, 8.7040),
    "Mahdia, Tunisia": (35.5047, 11.0622),
    "Sidi Bouzid, Tunisia": (35.0381, 9.4858),
    "Siliana, Tunisia": (36.0836, 9.3700),
    "Tozeur, Tunisia": (33.9197, 8.1335),
    "Zaghouan, Tunisia": (36.4026, 10.1425),
    "Kébili, Tunisia": (33.7049, 8.9690),
    "Manouba, Tunisia": (36.8108, 10.0978),
    
    "Tripoli, Libya": (32.8872, 13.1913),
    "Benghazi, Libya": (32.1167, 20.0683),
    "Misrata, Libya": (32.3744, 15.0925),
    "Tarhuna, Libya": (32.4349, 13.6332),
    "Al Khums, Libya": (32.6489, 14.2618),
    "Ajdabiya, Libya": (30.7554, 20.2263),
    "Zawiya, Libya": (32.7573, 12.7277),
    "Sirte, Libya": (31.2089, 16.5887),
    "Gharyan, Libya": (32.1667, 13.0167),
    "Tobruk, Libya": (32.0840, 23.9579),
    "Sabha, Libya": (27.0377, 14.4283),
    "Bani Walid, Libya": (31.7453, 13.9831),
    "Sabratha, Libya": (32.7932, 12.4842),
    "Derna, Libya": (32.7569, 22.6376),
    "Zliten, Libya": (32.4673, 14.5687),
    "Murzuq, Libya": (25.9154, 13.9182),
    "Kufra, Libya": (24.1781, 23.3105),
    "Ghat, Libya": (24.9647, 10.1800),
    "Nalut, Libya": (31.8698, 10.8497),
    "Awbari, Libya": (26.5877, 12.7846),
    
    "Khartoum, Sudan": (15.5007, 32.5599),
    "Omdurman, Sudan": (15.6445, 32.4777),
    "Khartoum Nord, Sudan": (15.6167, 32.5333),
    "Port-Soudan, Sudan": (19.6158, 37.2167),
    "Kassala, Sudan": (15.4515, 36.4000),
    "Obeid, Sudan": (13.1833, 30.2167),
    "Nyala, Sudan": (12.0540, 24.8781),
    "Gedaref, Sudan": (14.0354, 35.3838),
    "Wad Medani, Sudan": (14.4017, 33.5197),
    "El Fasher, Sudan": (13.6288, 25.3491),
    "Damazin, Sudan": (11.7891, 34.3592),
    "Dongola, Sudan": (19.1617, 30.4789),
    "Atbara, Sudan": (17.7017, 33.9858),
    "Sennar, Sudan": (13.5531, 33.6172),
    "Kosti, Sudan": (13.1629, 32.6634),
    "Rabak, Sudan": (13.1833, 32.7400),
    "Renk, Sudan": (11.7458, 32.7853),
    "Kadugli, Sudan": (11.0146, 29.7071),
    "Geneina, Sudan": (13.4527, 22.4473),
    "Malakali, Sudan": (9.5330, 31.6500),
    
    "Addis-Abeba, Ethiopia": (9.1450, 38.7451),
    "Dire Dawa, Ethiopia": (9.5919, 41.8669),
    "Nazret, Ethiopia": (8.5500, 39.2667),
    "Gondar, Ethiopia": (12.6000, 37.4667),
    "Mekele, Ethiopia": (13.4967, 39.4753),
    "Jimma, Ethiopia": (7.6833, 36.8333),
    "Bahir Dar, Ethiopia": (11.5933, 37.3917),
    "Dessie, Ethiopia": (11.1167, 39.6333),
    "Awassa, Ethiopia": (7.0667, 38.4667),
    "Debre Zeit, Ethiopia": (8.7333, 38.9833),
    "Harar, Ethiopia": (9.3167, 42.1167),
    "Nekemte, Ethiopia": (9.0833, 36.5500),
    "Debre Markos, Ethiopia": (10.3500, 37.7333),
    "Hosaena, Ethiopia": (7.5500, 37.8500),
    "Debre Birhan, Ethiopia": (9.6833, 39.5167),
    "Arba Minch, Ethiopia": (6.0333, 37.5500),
    "Asella, Ethiopia": (7.9500, 39.1333),
    "Gambela, Ethiopia": (8.2500, 34.5833),
    "Jijiga, Ethiopia": (9.3500, 42.8000),
    "Welkite, Ethiopia": (8.2833, 37.7833),
    
    "Nairobi, Kenya": (1.2921, 36.8219),
    "Mombasa, Kenya": (4.0435, 39.6682),
    "Nakuru, Kenya": (0.3031, 36.0800),
    "Eldoret, Kenya": (0.5143, 35.2698),
    "Kisumu, Kenya": (0.0917, 34.7680),
    "Thika, Kenya": (1.0332, 37.0692),
    "Malindi, Kenya": (3.2197, 40.1169),
    "Kitale, Kenya": (1.0167, 35.0000),
    "Garissa, Kenya": (0.4536, 39.6401),
    "Kakamega, Kenya": (0.2827, 34.7519),
    "Machakos, Kenya": (1.5177, 37.2634),
    "Meru, Kenya": (0.0500, 37.6500),
    "Nyeri, Kenya": (0.4167, 36.9500),
    "Kericho, Kenya": (0.3683, 35.2839),
    "Embu, Kenya": (0.5396, 37.4513),
    "Webuye, Kenya": (0.6000, 34.7667),
    "Mumias, Kenya": (0.3344, 34.4869),
    "Naivasha, Kenya": (0.7167, 36.4333),
    "Kilifi, Kenya": (3.6309, 39.8497),
    "Lamu, Kenya": (2.2717, 40.9020),
    
    "Kampala, Uganda": (0.3476, 32.5825),
    "Gulu, Uganda": (2.7667, 32.2833),
    "Lira, Uganda": (2.2333, 32.9000),
    "Mbarara, Uganda": (0.6167, 30.6500),
    "Jinja, Uganda": (0.4372, 33.2042),
    "Mbale, Uganda": (1.0833, 34.1833),
    "Mukono, Uganda": (0.3533, 32.7553),
    "Kasese, Uganda": (0.1833, 30.0833),
    "Masaka, Uganda": (0.3500, 31.7167),
    "Entebbe, Uganda": (0.0667, 32.4667),
    "Kitgum, Uganda": (3.2833, 32.8833),
    "Koboko, Uganda": (3.4167, 30.9500),
    "Soroti, Uganda": (1.7167, 33.6167),
    "Tororo, Uganda": (0.6833, 34.1833),
    "Fort Portal, Uganda": (0.6667, 30.2750),
    "Arua, Uganda": (3.0333, 30.9167),
    "Hoima, Uganda": (1.4333, 31.3500),
    "Moroto, Uganda": (2.5167, 34.6667),
    "Kabale, Uganda": (1.2500, 30.0000),
    "Bundibugyo, Uganda": (0.7167, 30.0667),
    
    "Dar es Salaam, Tanzania": (6.7924, 39.2083),
    "Mwanza, Tanzania": (2.5167, 32.9000),
    "Arusha, Tanzania": (3.3667, 36.6833),
    "Dodoma, Tanzania": (6.1629, 35.7516),
    "Mbeya, Tanzania": (8.9000, 33.4500),
    "Morogoro, Tanzania": (6.8167, 37.6667),
    "Tanga, Tanzania": (5.0689, 39.0982),
    "Tabora, Tanzania": (5.0167, 32.8000),
    "Kigoma, Tanzania": (4.8833, 29.6167),
    "Mtwara, Tanzania": (10.2692, 40.1836),
    "Zanzibar, Tanzania": (6.1659, 39.2026),
    "Iringa, Tanzania": (7.7667, 35.6833),
    "Singida, Tanzania": (4.8167, 34.7500),
    "Shinyanga, Tanzania": (3.6833, 33.4167),
    "Bukoba, Tanzania": (1.3333, 31.8167),
    "Musoma, Tanzania": (1.5000, 33.8000),
    "Lindi, Tanzania": (10.0000, 39.7167),
    "Sumbawanga, Tanzania": (7.9667, 31.6167),
    "Songea, Tanzania": (10.6833, 35.6500),
    "Kondoa, Tanzania": (4.9000, 35.7833),
    
    "Lusaka, Zambia": (15.3875, 28.3228),
    "Kitwe, Zambia": (12.8024, 28.2132),
    "Ndola, Zambia": (12.9587, 28.6366),
    "Kabwe, Zambia": (14.4469, 28.4464),
    "Chingola, Zambia": (12.5289, 27.8614),
    "Mufulira, Zambia": (12.5497, 28.2405),
    "Luanshya, Zambia": (13.1369, 28.4169),
    "Livingstone, Zambia": (17.8419, 25.8544),
    "Kasama, Zambia": (10.2167, 31.1833),
    "Chipata, Zambia": (13.6333, 32.6500),
    "Mazabuka, Zambia": (15.8500, 27.7500),
    "Choma, Zambia": (16.8000, 26.9833),
    "Kafue, Zambia": (15.7667, 28.1833),
    "Mongu, Zambia": (15.2500, 23.1333),
    "Solwezi, Zambia": (12.1667, 26.9000),
    "Mansa, Zambia": (11.1833, 28.9000),
    "Kalulushi, Zambia": (12.8417, 28.0947),
    "Kapiri Mposhi, Zambia": (13.9667, 28.6667),
    "Petauke, Zambia": (14.2500, 31.3167),
    "Mbala, Zambia": (8.8500, 31.3667),
    
    "Harare, Zimbabwe": (17.8252, 31.0335),
    "Bulawayo, Zimbabwe": (20.1677, 28.5833),
    "Chitungwiza, Zimbabwe": (18.0167, 31.0833),
    "Mutare, Zimbabwe": (18.9667, 32.6500),
    "Gweru, Zimbabwe": (19.4500, 29.8167),
    "Kwekwe, Zimbabwe": (18.9167, 29.8167),
    "Kadoma, Zimbabwe": (18.3333, 29.9167),
    "Masvingo, Zimbabwe": (20.0833, 30.8333),
    "Chinhoyi, Zimbabwe": (17.3667, 30.2000),
    "Marondera, Zimbabwe": (18.1833, 31.5500),
    "Zvishavane, Zimbabwe": (20.3333, 30.0667),
    "Bindura, Zimbabwe": (17.3000, 31.3333),
    "Beitbridge, Zimbabwe": (22.2167, 30.0000),
    "Redcliff, Zimbabwe": (19.0333, 29.7833),
    "Victoria Falls, Zimbabwe": (17.9333, 25.8167),
    "Hwange, Zimbabwe": (18.3667, 26.5000),
    "Chegutu, Zimbabwe": (18.1333, 30.1500),
    "Shurugwi, Zimbabwe": (19.6667, 30.0000),
    "Gokwe, Zimbabwe": (18.2167, 28.9333),
    "Rusape, Zimbabwe": (18.5333, 32.1167),
    
    "Johannesburg, South Africa": (26.2041, 28.0473),
    "Le Cap, South Africa": (33.9249, 18.4241),
    "Durban, South Africa": (29.8587, 31.0218),
    "Pretoria, South Africa": (25.7479, 28.2293),
    "Port Elizabeth, South Africa": (33.9608, 25.6022),
    "Bloemfontein, South Africa": (29.0852, 26.1596),
    "East London, South Africa": (33.0153, 27.9116),
    "Polokwane, South Africa": (23.9045, 29.4689),

# Amérique du Nord
    "New York, USA": (40.7128, -74.0060),
    "Los Angeles, USA": (34.0522, -118.2437),
    "Chicago, USA": (41.8781, -87.6298),
    "Houston, USA": (29.7604, -95.3698),
    "Phoenix, USA": (33.4484, -112.0740),
    "Philadelphia, USA": (39.9526, -75.1652),
    "San Antonio, USA": (29.4241, -98.4936),
    "San Diego, USA": (32.7157, -117.1611),
    "Dallas, USA": (32.7767, -96.7970),
    "San Jose, USA": (37.3382, -121.8863),
    "Austin, USA": (30.2672, -97.7431),
    "Jacksonville, USA": (30.3322, -81.6557),
    "Fort Worth, USA": (32.7555, -97.3308),
    "Columbus, USA": (39.9612, -82.9988),
    "San Francisco, USA": (37.7749, -122.4194),
    "Charlotte, USA": (35.2271, -80.8431),
    "Indianapolis, USA": (39.7684, -86.1581),
    "Seattle, USA": (47.6062, -122.3321),
    "Denver, USA": (39.7392, -104.9903),
    "Boston, USA": (42.3601, -71.0589),
    "El Paso, USA": (31.7619, -106.4850),
    "Nashville, USA": (36.1627, -86.7816),
    "Detroit, USA": (42.3314, -83.0458),
    "Oklahoma City, USA": (35.4676, -97.5164),
    "Portland, USA": (45.5152, -122.6784),
    "Las Vegas, USA": (36.1699, -115.1398),
    "Memphis, USA": (35.1495, -90.0490),
    "Louisville, USA": (38.2527, -85.7585),
    "Baltimore, USA": (39.2904, -76.6122),
    "Milwaukee, USA": (43.0389, -87.9065),
    "Albuquerque, USA": (35.0844, -106.6504),
    "Tucson, USA": (32.2226, -110.9747),
    "Fresno, USA": (36.7378, -119.7871),
    "Sacramento, USA": (38.5816, -121.4944),
    "Kansas City, USA": (39.0997, -94.5786),
    "Mesa, USA": (33.4152, -111.8315),
    "Atlanta, USA": (33.7490, -84.3880),
    "Virginia Beach, USA": (36.8529, -75.9780),
    "Omaha, USA": (41.2565, -95.9345),
    "Colorado Springs, USA": (38.8339, -104.8214),
    "Raleigh, USA": (35.7796, -78.6382),
    "Miami, USA": (25.7617, -80.1918),
    "Oakland, USA": (37.8044, -122.2711),
    "Minneapolis, USA": (44.9778, -93.2650),
    "Tulsa, USA": (36.1540, -95.9928),
    "Cleveland, USA": (41.4993, -81.6944),
    "Wichita, USA": (37.6872, -97.3301),
    "Arlington, USA": (32.7357, -97.1081),
    "Tampa, USA": (27.9506, -82.4572),
    "Bakersfield, USA": (35.3733, -119.0187),
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
    col1, col2, col3 = st.columns([1,1,3])
    
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
                        height: 3px;
                        width: 100%;
                        margin-bottom: 0px;
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
    
