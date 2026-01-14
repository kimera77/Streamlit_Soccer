import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (API keys, etc.)
load_dotenv()

import utils.data_loader as loader
from utils.config import PAGE_CONFIG



st.set_page_config(**PAGE_CONFIG)

# Limpiar caché al inicio SOLO si es la primera vez que se carga la app en esta sesión
# Esto fuerza a recargar los datos frescos desde load_data()
if 'cache_cleared' not in st.session_state:
    st.cache_data.clear()
    st.session_state.cache_cleared = True

IMAGE_URL = 'https://media.istockphoto.com/id/639387036/es/foto/hombre-de-jugador-de-f%C3%BAtbol-aislado.jpg?s=612x612&w=0&k=20&c=Kiwcqtuu9V1MrsSRj8UeorzJ_buvOCvGe5D4JfFEtSQ='
st.markdown(
    f"""
    <style>
    /* Estilos para el fondo principal de la aplicación */
    body, .stApp {{
       background: #FFFFFF !important;
       color: #000000 !important;
    }}

    /* 1. Selector para el contenedor principal del sidebar (Fondo de Imagen y SEPARADOR) */
    [data-testid="stSidebar"] {{
       background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), url("{IMAGE_URL}");
       background-size: cover; 
       background-position: center; 
       background-repeat: no-repeat;
       
       /* === NUEVA SOMBRA DE SEPARACIÓN HACIA LA DERECHA === */
       /* La sombra simula una línea más gruesa y suave */
       box-shadow: 6px 0 8px 0 rgba(0, 0, 0, 0.7); /* Sombra negra, 6px a la derecha, desenfoque de 8px */
       /* NOTA: Puedes ajustar el primer número (6px) para hacer la sombra más ancha */
       /* El valor 'rgba(0, 0, 0, 0.7)' define un color negro con 70% de opacidad */
       /* Se elimina border-right, ya que box-shadow lo reemplaza */
    }}

    /* 2. Selector para el contenido interno (Quita el fondo gris) */
    [data-testid="stSidebarContent"] {{
       background-color: transparent !important;
       color: #000000 !important;
    }}
    
    /* 3. Estilos específicos para el texto (Header y Radio) */
    
    /* Título/Header del sidebar */
    [data-testid="stSidebar"] h2 {{ 
       color: #000000 !important;
       font-size: 24px !important;
       text-shadow: 1px 1px 2px #FFFFFF;
    }}
    
    /* Opciones de Radio y Etiqueta */
    [data-testid="stSidebar"] .st-cd label,
    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .st-cd div p {{
       color: #000000 !important; 
       font-size: 18px !important;
       font-weight: bold; 
       text-shadow: 1px 1px 2px #FFFFFF;
    }}

    /* Texto genérico (st.markdown) */
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
    st.markdown("<br><br>", unsafe_allow_html=True)  # Espacio superior adicional
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
    

    
# Función para cargar datos con caché
# @st.cache_data: decorador que almacena en caché el resultado de la función
# Evita recargar los datos en cada interacción, mejorando el rendimiento
@st.cache_data
def get_data_cached():
    """Cached wrapper around utils.data_loader.load_data to avoid recursion."""
    return loader.load_data()

try:
    # load_data() ahora retorna (df, load_info)
    result = get_data_cached()
    
    # Manejar tanto el formato antiguo (solo df) como el nuevo (df, load_info)
    if isinstance(result, tuple):
        df, load_info = result
        # Guardamos load_info en session_state para que esté disponible globalmente
        st.session_state.load_info = load_info
    else:
        # Compatibilidad con caché antiguo
        df = result
        st.session_state.load_info = {
            'csv_already_existed': None,
            'processing_time': 0.0,
            'timestamp': None
        }
    
    # Guardar df en session_state para acceso global (necesario para iaPlayers.py)
    st.session_state.df = df

    if page == "🏠 Inicio":
        # Mostrar título y descripción solo en la página de inicio
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