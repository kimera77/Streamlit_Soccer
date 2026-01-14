"""
Punto de entrada para Hugging Face Spaces.
Este archivo importa y ejecuta la aplicación principal desde panel/src/app.py
"""
import os
import sys

# Añadir panel/src al path de Python para poder importar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
panel_src = os.path.join(current_dir, 'panel', 'src')
sys.path.insert(0, panel_src)

# Importar streamlit y las dependencias necesarias
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (API keys, etc.)
# En Hugging Face Spaces, las variables se cargan automáticamente
try:
    load_dotenv()
except:
    pass  # No hay problema si no existe .env (ej: en Hugging Face)

# Ahora importamos desde utils (ya está en el path)
import utils.data_loader as loader
from utils.config import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# Limpiar caché al inicio SOLO si es la primera vez que se carga la app en esta sesión
if 'cache_cleared' not in st.session_state:
    st.cache_data.clear()
    st.session_state.cache_cleared = True

IMAGE_URL = 'https://media.istockphoto.com/id/639387036/es/foto/hombre-de-jugador-de-f%C3%BAtbol-aislado.jpg?s=612x612&w=0&k=20&c=Kiwcqtuu9V1MrsSRj8UeorzJ_buvOCvGe5D4JfFEtSQ='
st.markdown(
    f"""
    <style>
    body, .stApp {{
       background: #FFFFFF !important;
       color: #000000 !important;
    }}
    [data-testid="stSidebar"] {{
       background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), url("{IMAGE_URL}");
       background-size: cover; 
       background-position: center; 
       background-repeat: no-repeat;
       box-shadow: 6px 0 8px 0 rgba(0, 0, 0, 0.7);
    }}
    [data-testid="stSidebarContent"] {{
       background-color: transparent !important;
       color: #000000 !important;
    }}
    [data-testid="stSidebar"] h2 {{ 
       color: #000000 !important;
       font-size: 24px !important;
       text-shadow: 1px 1px 2px #FFFFFF;
    }}
    [data-testid="stSidebar"] .st-cd label,
    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .st-cd div p {{
       color: #000000 !important; 
       font-size: 18px !important;
       font-weight: bold; 
       text-shadow: 1px 1px 2px #FFFFFF;
    }}
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stText p {{
       color: #000000 !important; 
       font-size: 18px !important;
       font-weight: bold; 
       text-shadow: 1px 1px 2px #FFFFFF;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("⚽ Navegación")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #000000; margin: 10px 0;'>", unsafe_allow_html=True)
    
    page = st.radio(
        "Ir a",
        (
            "🏠 Inicio",
            "👤 Análisis por Jugadores",
            "👕 Análisis por Equipo",
            "🏆 Análisis por Liga",
            "🪄 IA Players",
        ),
    )
    
    st.markdown("<hr style='border: 1px solid #000000; margin: 10px 0;'>", unsafe_allow_html=True)

@st.cache_data
def get_data_cached():
    """Cached wrapper around utils.data_loader.load_data to avoid recursion."""
    return loader.load_data()

try:
    result = get_data_cached()
    
    if isinstance(result, tuple):
        df, load_info = result
        st.session_state.load_info = load_info
    else:
        df = result
        st.session_state.load_info = {
            'csv_already_existed': None,
            'processing_time': 0.0,
            'timestamp': None
        }
    
    st.session_state.df = df

    if page == "🏠 Inicio":
        st.title("⚽ Jugadores de Fútbol - Temporada 2015-2016")
        st.markdown("""
            Esta aplicación interactiva te permite explorar y analizar datos de **jugadores profesionales de fútbol** 
            de la temporada 2015-2016. Descubre los mejores talentos, compara atributos técnicos y descubre 
            tendencias en las principales ligas europeas. \n
            La estadistica se basa en un rango de valores que va entre 0 y 100, donde 100 representa la máxima habilidad o rendimiento en esa categoría específica. 
            """)
        st.markdown("---")
        
        from ui.home import render_home_page
        render_home_page(df)
    elif page == "👤 Análisis por Jugadores":
        from ui.players import render_players_page
        render_players_page(df)
    elif page == "👕 Análisis por Equipo":
        from ui.teams import render_teams_page
        render_teams_page(df)
    elif page == "🏆 Análisis por Liga":
        from ui.leagues import render_leagues_page
        render_leagues_page(df)
    elif page == "🪄 IA Players":
        from ui.iaPlayers import render_top_players_page
        render_top_players_page()

except Exception as e:   
    st.error(f"Error al cargar los datos: {e}")
    st.exception(e)  # Mostrar el traceback completo para debugging

