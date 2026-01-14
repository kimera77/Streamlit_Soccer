import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import get_data_info, delete_csv
import pandas as pd
import numpy as np

def render_home_page(df):

    # Obtener información del dataset
    info = get_data_info(df)

    # Métricas principales con diseño deportivo
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="👥 Total de Jugadores",
            value=f"{info['total_jugadores']:,}",
            delta=None,
            help="Jugadores únicos en la base de datos"
        )
    with col2:
        st.metric(
            label="⚽ Equipos",
            value=f"{info['total_equipos']:,}",
            delta=None,
            help="Equipos profesionales registrados"
        )
    with col3:
        st.metric(
            label="🏆 Ligas Europeas",
            value=f"{info['total_ligas']}",
            delta=None,
            help="Ligas profesionales europeas en el dataset"
        )

    st.markdown("---")

    # Segunda fila de métricas - Estadísticas físicas
    col1, col2, col3 = st.columns(3)

    with col1:
        if info['edad_promedio']:
            st.metric(
                label="📅 Edad Promedio",
                value=f"{info['edad_promedio']:.1f} años",
                delta=None,
                help="Edad media de los jugadores en 2016"
            )
    
    with col2:
        if info['altura_promedio']:
            st.metric(
                label="📏 Altura Media",
                value=f"{info['altura_promedio']:.1f} cm",
                delta=None,
                help="Altura promedio de todos los jugadores"
            )
    
    with col3:
        if info['peso_promedio']:
            st.metric(
                label="⚖️ Peso Medio",
                value=f"{info['peso_promedio']:.1f} kg",
                delta=None,
                help="Peso promedio de todos los jugadores"
            )

    st.markdown("---")

    # Función callback que se ejecuta ANTES del render
    def handle_regenerate():
        delete_csv()
        st.cache_data.clear()
        # Limpiar también load_info del session_state para forzar recarga
        if 'load_info' in st.session_state:
            del st.session_state.load_info
        st.session_state.show_regen_msg = True
    
    # Contenedor con borde simple
    with st.container(border=True):
        # Información del Sistema
        st.markdown("#### 🔧 Información del Sistema")
        
        # Obtener load_info desde session_state (ya fue guardado en app.py)
        load_info = st.session_state.get('load_info', {
            'csv_already_existed': None,
            'processing_time': 0.0,
            'timestamp': None
        })
        

        # Determinar qué mensaje mostrar
        if 'show_regen_msg' in st.session_state and st.session_state.show_regen_msg:
            # Acabamos de regenerar manualmente
            st.success(f"✅ **CSV Regenerado Exitosamente** - Procesado desde SQLite en **{load_info['processing_time']:.2f}s**")
            # Limpiar el flag
            del st.session_state.show_regen_msg
        elif load_info['csv_already_existed'] == False:
            # Primera generación del CSV (app inició sin CSV)
            # Usamos == False en lugar de not para distinguir de None
            st.success(f"⚙️ **Procesamiento Completo** - CSV generado desde SQLite en **{load_info['processing_time']:.2f}s**")
        elif load_info['csv_already_existed'] == True:
            # CSV ya existía - carga normal
            st.info(f"🚀 **Carga Rápida** - CSV existente cargado en **{load_info['processing_time']:.3f}s**")
            st.caption("✨ Los datos ya estaban procesados. No fue necesario regenerar desde SQLite.")
        else:
            # Caso inesperado (csv_already_existed == None)
            st.warning("⚠️ Estado de carga desconocido")
        
        st.markdown("**📥 Carga de Datos:**")
        st.write("· Leer SQLITE\n · Limpiar datos\n · Filtrar año 2016\n · Unir tablas\n · Limpiar datos")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón con callback - el callback se ejecuta ANTES de que el script se re-ejecute
        st.markdown("""
            <style>
            /* Estilos para el botón de regenerar */
            .stButton > button {
                background-color: #E8E8E8 !important;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3) !important;
            }
            .stButton > button:hover {
                background-color: #D0D0D0 !important;
                box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.4) !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.button(
            "🔄 Borrar CSV → Limpiar Caché → Recargar Página", 
            type="secondary",
            on_click=handle_regenerate
        )
