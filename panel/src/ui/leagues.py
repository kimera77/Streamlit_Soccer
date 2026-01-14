import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_leagues_page(df):
    """
    Página de análisis por liga con comparaciones y estadísticas.
    """
    
    st.markdown("## ⚽ Análisis por Liga")
    st.markdown("Compara el nivel de las diferentes ligas europeas en la temporada 2015-2016.")
    
    st.markdown("---")
    
    # ========== SECCIÓN 1: OVERVIEW DE LIGAS ==========
    st.markdown("### 🏆 Comparativa General de Ligas")
    st.markdown("Este gráfico muestra el **rating promedio** de todos los jugadores en cada liga. Un rating más alto indica que la liga tiene jugadores de mayor calidad en general. Las ligas con más jugadores de élite (rating ≥ 80) suelen tener promedios más altos.")
    
    if 'league_name' in df.columns and 'overall_rating' in df.columns:
        # Calcular estadísticas por liga
        stats_liga = df.groupby('league_name').agg(
            rating_medio=('overall_rating', 'mean'),
            rating_max=('overall_rating', 'max'),
            num_jugadores=('player_name', 'count'),
            jugadores_elite=('overall_rating', lambda x: (x >= 80).sum())
        ).reset_index()
        
        stats_liga['pct_elite'] = (stats_liga['jugadores_elite'] / stats_liga['num_jugadores']) * 100
        stats_liga = stats_liga.sort_values('rating_medio', ascending=False)
        
        # Gráfico de barras con rating medio por liga (pantalla completa)
        fig_barras = px.bar(
            stats_liga,
            x='league_name',
            y='rating_medio',
            title='Rating Promedio por Liga',
            labels={'league_name': 'Liga', 'rating_medio': 'Rating Promedio'},
            color='rating_medio',
            color_continuous_scale='RdYlGn',
            text='rating_medio'
        )
        
        fig_barras.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_barras.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            yaxis=dict(range=[60, stats_liga['rating_medio'].max() + 2])
        )
        
        st.plotly_chart(fig_barras, use_container_width=True)
    
    st.markdown("---")
    
    # ========== SECCIÓN 2: COMPARADOR DE LIGAS INTERACTIVO ==========
    st.markdown("### 🔍 Detalle Liga")
    
    if 'league_name' in df.columns and 'country_name' in df.columns:
        # Crear lista de ligas con país para el selector
        ligas_con_pais = df[['country_name', 'league_name']].drop_duplicates()
        ligas_con_pais['display_name'] = ligas_con_pais['country_name'] + ' - ' + ligas_con_pais['league_name']
        ligas_con_pais = ligas_con_pais.sort_values('display_name')
        
        # Buscar el índice de Spain LIGA BBVA como default
        lista_ligas = ligas_con_pais['display_name'].tolist()
        default_index = 0
        for idx, nombre in enumerate(lista_ligas):
            if 'Spain LIGA BBVA' in nombre or 'LIGA BBVA' in nombre:
                default_index = idx
                break
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            liga_display = st.selectbox(
                "🏆 Selecciona una liga:",
                options=lista_ligas,
                index=default_index,
                key='liga_comparador'
            )
            
            # Extraer el nombre de la liga del display
            liga_seleccionada = ligas_con_pais[ligas_con_pais['display_name'] == liga_display]['league_name'].iloc[0]
        
        if liga_seleccionada:
            df_liga = df[df['league_name'] == liga_seleccionada]
            
            # Métricas principales
            st.markdown(f"#### 📈 Estadísticas: {liga_seleccionada}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                num_equipos = df_liga['team_long_name'].nunique()
                st.metric("Equipos", f"{num_equipos}")
            
            with col2:
                st.metric("Jugadores", f"{len(df_liga):,}")
            
            with col3:
                rating_medio = df_liga['overall_rating'].mean()
                st.metric("Rating Medio", f"{rating_medio:.1f}")
            
            with col4:
                rating_max = df_liga['overall_rating'].max()
                mejor_jugador = df_liga[df_liga['overall_rating'] == rating_max]['player_name'].iloc[0]
                st.metric("Mejor Jugador", mejor_jugador, f"{rating_max}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Top 3 jugadores (presentación horizontal) y sin histograma
            st.markdown(f"#### 🌟 Top 3 Jugadores")

            top_3 = df_liga.nlargest(3, 'overall_rating')[['player_name', 'overall_rating', 'team_long_name']]

            cols_top = st.columns(len(top_3))
            for i, (_, row) in enumerate(top_3.iterrows()):
                with cols_top[i]:
                    # Usamos metric para destacar el rating; el nombre va como etiqueta
                    st.metric(label=row['player_name'], value=f"{int(row['overall_rating'])}")
                    st.caption(f"📍 {row['team_long_name']}")
    
    st.markdown("---")
    
    # ========== SECCIÓN 4: ANÁLISIS DE EQUIPOS POR LIGA ==========
    st.markdown("### 🏟️ Análisis de Equipos por Liga")
    st.markdown("Descubre qué equipos dominan cada liga y cómo se distribuye el talento entre las diferentes plantillas.")
    
    if 'league_name' in df.columns and 'team_long_name' in df.columns:
        # Obtener lista de ligas únicas con país
        ligas_con_pais_eq = df[['country_name', 'league_name']].drop_duplicates()
        ligas_con_pais_eq['display_name'] = ligas_con_pais_eq['country_name'] + ' - ' + ligas_con_pais_eq['league_name']
        ligas_con_pais_eq = ligas_con_pais_eq.sort_values('display_name')
        
        # Buscar el índice de Spain LIGA BBVA como default
        lista_ligas_eq = ligas_con_pais_eq['display_name'].tolist()
        default_index_eq = 0
        for idx, nombre in enumerate(lista_ligas_eq):
            if 'Spain LIGA BBVA' in nombre or 'LIGA BBVA' in nombre:
                default_index_eq = idx
                break
        
        liga_eq_display = st.selectbox(
            "🏆 Selecciona una liga:",
            options=lista_ligas_eq,
            index=default_index_eq,
            key='liga_equipos'
        )
        
        # Extraer el nombre de la liga
        liga_equipos = ligas_con_pais_eq[ligas_con_pais_eq['display_name'] == liga_eq_display]['league_name'].iloc[0]
        
        if liga_equipos:
            df_liga_eq = df[df['league_name'] == liga_equipos]
            
            # Estadísticas por equipo
            stats_equipos = df_liga_eq.groupby('team_long_name').agg(
                rating_medio=('overall_rating', 'mean'),
                num_jugadores=('player_name', 'count'),
                rating_max=('overall_rating', 'max'),
                mejor_jugador=('player_name', lambda x: df_liga_eq[df_liga_eq['player_name'].isin(x)].nlargest(1, 'overall_rating')['player_name'].iloc[0] if len(x) > 0 else '')
            ).reset_index()
            
            stats_equipos = stats_equipos.sort_values('rating_medio', ascending=False)
            
            # Resumen de la liga
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🏆 Mejor Equipo", stats_equipos.iloc[0]['team_long_name'])
                st.caption(f"Rating: {stats_equipos.iloc[0]['rating_medio']:.1f}")
            
            with col2:
                st.metric("⭐ Equipo más Elite", stats_equipos.iloc[0]['team_long_name'])
                st.caption(f"Rating máx: {stats_equipos.iloc[0]['rating_max']}")
            
            with col3:
                total_equipos = len(stats_equipos)
                st.metric("🏟️ Total Equipos", total_equipos)
            
            with col4:
                diferencia = stats_equipos.iloc[0]['rating_medio'] - stats_equipos.iloc[-1]['rating_medio']
                st.metric("📊 Brecha 1º vs Último", f"{diferencia:.1f}")
                st.caption("Diferencia de rating")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico de barras con TODOS los equipos
            fig_equipos = px.bar(
                stats_equipos,  # Todos los equipos
                x='rating_medio',
                y='team_long_name',
                orientation='h',
                title=f'Ranking de Equipos: {liga_equipos}',
                labels={'rating_medio': 'Rating Promedio', 'team_long_name': 'Equipo'},
                color='rating_medio',
                color_continuous_scale='RdYlGn',
                text='rating_medio',
                hover_data={'num_jugadores': True, 'rating_max': True}
            )

            # Altura dinámica según cantidad de equipos (aprox 30 px por barra + margen)
            altura_dinamica = max(420, 30 * len(stats_equipos) + 100)
            fig_equipos.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_equipos.update_layout(
                height=altura_dinamica,
                showlegend=False,
                xaxis=dict(range=[stats_equipos['rating_medio'].min() - 2, stats_equipos['rating_medio'].max() + 2])
            )

            st.plotly_chart(fig_equipos, use_container_width=True)
