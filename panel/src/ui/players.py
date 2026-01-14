import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_players_page(df):
    """
    Página de análisis detallado de jugadores con distribuciones y estadísticas.
    """
    
    st.markdown("## 👤 Análisis Detallado de Jugadores")
    st.markdown("Explora estadísticas y distribuciones de los jugadores de la temporada 2015-2016.")
    
    st.markdown("---")
    
    # ========== SECCIÓN 1: PICO DE RENDIMIENTO POR EDAD ==========
    st.markdown("### 🎯 El Pico de Rendimiento: Edad vs Rating")
    st.markdown("Con el gráfico de rangos de habilidad podemos observar que solo el **5.8% de todos los jugadores se consideran élite** (rating superior a 80).  \nEl análisis revela tambien que **a qué edad los futbolistas alcanzan su máximo nivel**, con el pico de rendimiento entre los 25-30 años.")
    
    if 'overall_rating' in df.columns and 'birthday' in df.columns:
        # Calcular edad
        df_edad = df.copy()
        df_edad['birthday'] = pd.to_datetime(df_edad['birthday'], errors='coerce')
        df_edad['edad'] = (pd.Timestamp('2016-12-31') - df_edad['birthday']).dt.days / 365.25
        df_edad = df_edad.dropna(subset=['edad', 'overall_rating'])
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📊 Rangos de Habilidad")
            
            # Crear categorías de habilidad
            df_temp = df.copy()
            df_temp['categoria'] = pd.cut(
                df_temp['overall_rating'], 
                bins=[0, 60, 70, 80, 100],
                labels=['📉 Bajo (0-60)', '📊 Medio (60-70)', '📈 Alto (70-80)', '🌟 Elite (80+)']
            )
            
            categoria_counts = df_temp['categoria'].value_counts().sort_index()
            
            for cat, count in categoria_counts.items():
                percentage = (count / len(df_temp)) * 100
                st.markdown(f"**{cat}**")
                st.progress(percentage / 100)
                st.caption(f"{count:,} jugadores ({percentage:.1f}%)")
            
            st.markdown("<br>", unsafe_allow_html=True)
             
            # Calcular estadísticas del pico con ponderación por número de jugadores
            edad_int = df_edad['edad'].astype(int)
            rating_por_edad = df_edad.groupby(edad_int).agg(
                rating_medio=('overall_rating', 'mean'),
                num_jugadores=('overall_rating', 'count')
            )
            
            # Calcular score ponderado: rating_medio * log(num_jugadores + 1)
            # Esto da más peso a edades con más jugadores sin eliminar las minoritarias
            rating_por_edad['score_ponderado'] = rating_por_edad['rating_medio'] * np.log1p(rating_por_edad['num_jugadores'])
            
            edad_pico = rating_por_edad['score_ponderado'].idxmax()
            rating_pico = rating_por_edad.loc[edad_pico, 'rating_medio']
            num_jugadores_pico = rating_por_edad.loc[edad_pico, 'num_jugadores']
            
            st.markdown("#### 🏆 Pico de Rendimiento")
            col_edad, col_rating = st.columns(2)
            with col_edad:
                st.metric("Edad del Pico", f"{int(edad_pico)} años")
            with col_rating:
                st.metric("Rating Promedio", f"{rating_pico:.1f}")
        
        with col2:
            # Filtro para resaltar jugador (encima del gráfico)
            # Ordenar jugadores por overall rating descendente
            jugadores_ordenados = df_edad.sort_values('overall_rating', ascending=False)['player_name'].unique().tolist()
            
            jugador_resaltar = st.selectbox(
                "🔍 Resaltar jugador en el gráfico:",
                options=['Ninguno'] + jugadores_ordenados,
                key='jugador_resaltar_edad'
            )
            # Scatter plot con línea de tendencia
            fig_scatter = px.scatter(
                df_edad,
                x='edad',
                y='overall_rating',
                title='Rendimiento por Edad: ¿Cuándo alcanzan su pico los jugadores?',
                labels={'edad': 'Edad (años)', 'overall_rating': 'Overall Rating'},
                opacity=0.4,
                color='overall_rating',
                color_continuous_scale='RdYlGn',
                trendline='lowess',
                trendline_color_override='red',
                hover_data={'player_name': True, 'edad': ':.1f', 'overall_rating': True}
            )
            
            fig_scatter.update_layout(
                height=450,
                showlegend=False
            )
            
            fig_scatter.add_hline(
                y=80, 
                line_dash="dash", 
                line_color="gold",
                annotation_text="Nivel Elite (80+)",
                annotation_position="right"
            )
            
            # Si hay un jugador seleccionado, resaltarlo
            if jugador_resaltar and jugador_resaltar != 'Ninguno':
                jugador_data = df_edad[df_edad['player_name'] == jugador_resaltar].iloc[0]
                
                # Añadir punto grande para el jugador resaltado
                fig_scatter.add_trace(go.Scatter(
                    x=[jugador_data['edad']],
                    y=[jugador_data['overall_rating']],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='red',
                        symbol='star',
                        line=dict(color='white', width=2)
                    ),
                    name=jugador_resaltar,
                    showlegend=False,
                    hovertemplate=f"<b>{jugador_resaltar}</b><br>Edad: {jugador_data['edad']:.1f}<br>Rating: {jugador_data['overall_rating']}<extra></extra>"
                ))
                
                # Añadir anotación
                fig_scatter.add_annotation(
                    x=jugador_data['edad'],
                    y=jugador_data['overall_rating'],
                    text=f"<b>{jugador_resaltar}</b><br>Edad: {jugador_data['edad']:.1f}<br>Rating: {jugador_data['overall_rating']}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#ff0000",
                    ax=60,
                    ay=-60,
                    bgcolor="rgba(255, 255, 255, 0.9)",
                    bordercolor="#ff0000",
                    borderwidth=2
                )
            
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    
    # ========== SECCIÓN 2: COMPARADOR DE JUGADORES CON RADAR ==========
    st.markdown("### ⚡ Comparador de Atributos entre Jugadores")
    
    # Crear 3 columnas: Selectores (más estrecha) | Radar Técnico | Radar Físico
    col1, col2, col3 = st.columns([0.6, 1.9, 1.5])
    
    # COLUMNA 1: Selectores de jugadores
    with col1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Ordenar jugadores por rating
        jugadores_disponibles = sorted(df['player_name'].unique())
        
        # Inicializar valores por defecto en session_state
        if 'radar_jugador_1' not in st.session_state:
            st.session_state.radar_jugador_1 = 'Lionel Messi' if 'Lionel Messi' in jugadores_disponibles else jugadores_disponibles[0]
        
        if 'radar_jugador_2' not in st.session_state:
            st.session_state.radar_jugador_2 = 'Cristiano Ronaldo' if 'Cristiano Ronaldo' in jugadores_disponibles else jugadores_disponibles[1]
        
        # Asegurar que los valores guardados existen en la lista
        index_j1 = jugadores_disponibles.index(st.session_state.radar_jugador_1) if st.session_state.radar_jugador_1 in jugadores_disponibles else 0
        index_j2 = jugadores_disponibles.index(st.session_state.radar_jugador_2) if st.session_state.radar_jugador_2 in jugadores_disponibles else 1
        
        jugador_1 = st.selectbox(
            "🥇 Jugador 1:",
            options=jugadores_disponibles,
            index=index_j1,
            key='radar_jugador_1'
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        jugador_2 = st.selectbox(
            "🥈 Jugador 2:",
            options=jugadores_disponibles,
            index=index_j2,
            key='radar_jugador_2'
        )
    
    # COLUMNA 2: Gráfico Radar Técnico/Ofensivo
    with col2:
        st.markdown("#### ⚔️ Habilidades Técnicas/Ofensivas")
        
        # Atributos técnicos y ofensivos
        atributos_tecnicos = ['dribbling', 'finishing', 'free_kick_accuracy', 'heading_accuracy', 'shot_power', 'penalties']
        atributos_tecnicos_disponibles = [attr for attr in atributos_tecnicos if attr in df.columns]
        
        if atributos_tecnicos_disponibles and jugador_1 and jugador_2:
            # Obtener datos de ambos jugadores
            datos_j1_tec = df[df['player_name'] == jugador_1][atributos_tecnicos_disponibles].iloc[0]
            datos_j2_tec = df[df['player_name'] == jugador_2][atributos_tecnicos_disponibles].iloc[0]
            
            nombres_tecnicos = {
                'dribbling': 'Regate',
                'finishing': 'Finalización',
                'free_kick_accuracy': 'Tiros Libres',
                'heading_accuracy': 'Juego Aéreo',
                'shot_power': 'Potencia Tiro',
                'penalties': 'Penaltis'
            }
            
            fig_radar_tec = go.Figure()
            
            # Jugador 1
            fig_radar_tec.add_trace(go.Scatterpolar(
                r=datos_j1_tec.values,
                theta=[nombres_tecnicos.get(attr, attr) for attr in atributos_tecnicos_disponibles],
                fill='toself',
                name=jugador_1,
                line=dict(color='#1f77b4', width=2),
                fillcolor='rgba(31, 119, 180, 0.3)'
            ))
            
            # Jugador 2
            fig_radar_tec.add_trace(go.Scatterpolar(
                r=datos_j2_tec.values,
                theta=[nombres_tecnicos.get(attr, attr) for attr in atributos_tecnicos_disponibles],
                fill='toself',
                name=jugador_2,
                line=dict(color='#ff7f0e', width=2),
                fillcolor='rgba(255, 127, 14, 0.3)'
            ))
            
            fig_radar_tec.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[50, 100]
                    )
                ),
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig_radar_tec, use_container_width=True)
    
    # COLUMNA 3: Gráfico Radar Físico
    with col3:
        st.markdown("#### 💪 Atributos Físicos")
        
        # Atributos físicos
        atributos_fisicos = ['acceleration', 'sprint_speed', 'agility', 'jumping', 'stamina']
        atributos_fisicos_disponibles = [attr for attr in atributos_fisicos if attr in df.columns]
        
        if atributos_fisicos_disponibles and jugador_1 and jugador_2:
            # Obtener datos de ambos jugadores
            datos_j1_fis = df[df['player_name'] == jugador_1][atributos_fisicos_disponibles].iloc[0]
            datos_j2_fis = df[df['player_name'] == jugador_2][atributos_fisicos_disponibles].iloc[0]
            
            nombres_fisicos = {
                'acceleration': 'Aceleración',
                'sprint_speed': 'Velocidad',
                'agility': 'Agilidad',
                'jumping': 'Salto',
                'stamina': 'Resistencia'
            }
            
            fig_radar_fis = go.Figure()
            
            # Jugador 1
            fig_radar_fis.add_trace(go.Scatterpolar(
                r=datos_j1_fis.values,
                theta=[nombres_fisicos.get(attr, attr) for attr in atributos_fisicos_disponibles],
                fill='toself',
                name=jugador_1,
                line=dict(color='#1f77b4', width=2),
                fillcolor='rgba(31, 119, 180, 0.3)'
            ))
            
            # Jugador 2
            fig_radar_fis.add_trace(go.Scatterpolar(
                r=datos_j2_fis.values,
                theta=[nombres_fisicos.get(attr, attr) for attr in atributos_fisicos_disponibles],
                fill='toself',
                name=jugador_2,
                line=dict(color='#ff7f0e', width=2),
                fillcolor='rgba(255, 127, 14, 0.3)'
            ))
            
            fig_radar_fis.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[50, 100]
                    )
                ),
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig_radar_fis, use_container_width=True)

    st.markdown("---")
    
    # ========== SECCIÓN 3: DISTRIBUCIÓN DE EDADES ==========
    st.markdown("### 📅 Distribución de Edades")
  
    if 'birthday' in df.columns:
        df_edad = df.copy()
        df_edad['birthday'] = pd.to_datetime(df_edad['birthday'], errors='coerce')
        df_edad['edad'] = (pd.Timestamp('2016-12-31') - df_edad['birthday']).dt.days / 365.25
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Histograma de edades
            fig_edad = px.histogram(
                df_edad,
                x='edad',
                nbins=30,
                title='Distribución de Edades',
                labels={'edad': 'Edad (años)', 'count': 'Número de Jugadores'},
                color_discrete_sequence=['#2ecc71']
            )
            fig_edad.update_layout(height=400)
            st.plotly_chart(fig_edad, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Rangos de Edad")
            
            # Categorías por edad
            df_edad['categoria_edad'] = pd.cut(
                df_edad['edad'],
                bins=[0, 21, 25, 30, 100],
                labels=['🌱 Sub-21', '🔥 21-25', '💪 26-30', '🎓 30+']
            )
            
            edad_counts = df_edad['categoria_edad'].value_counts().sort_index()
            
            for cat, count in edad_counts.items():
                percentage = (count / len(df_edad)) * 100
                st.markdown(f"**{cat}**")
                st.progress(percentage / 100)
                st.caption(f"{count:,} jugadores ({percentage:.1f}%)")
    
    st.markdown("---")
    
    # ========== SECCIÓN 4: ALTURA VS RATING ==========
    st.markdown("### 📏 Relación Altura vs Rating")
    
    if 'height' in df.columns and 'overall_rating' in df.columns:
        # Scatter plot
        fig_scatter = px.scatter(
            df,
            x='height',
            y='overall_rating',
            title='¿La altura influye en el rating?',
            labels={'height': 'Altura (cm)', 'overall_rating': 'Overall Rating'},
            opacity=0.5,
            color='overall_rating',
            color_continuous_scale='Viridis'
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Calcular correlación
        correlacion = df['height'].corr(df['overall_rating'])
        if abs(correlacion) < 0.3:
            st.info(f"📊 Correlación: {correlacion:.3f} - No hay una relación significativa entre altura y rating.")
        else:
            st.success(f"📊 Correlación: {correlacion:.3f} - Existe cierta relación entre altura y rating.")
    
    st.markdown("---")

    # ========== TOP RANKING DE JUGADORES CON FILTROS ==========
    st.markdown("### 🏅 Ranking de Mejores Jugadores")
    st.markdown("Explora los mejores jugadores por diferentes categorías con filtros avanzados.")
    
    # Filtros en columnas (Equipo primero, luego Liga)
    col1, col2 = st.columns(2)
    
    # Primero: Filtro por Liga (para poder filtrar equipos dinámicamente)
    with col2:
        # Filtro por liga: "País - Liga"
        if 'league_name' in df.columns and 'country_name' in df.columns:
            # Crear diccionario con formato "País - Liga" -> nombre real liga
            ligas_dict = {}
            ligas_dict["Todas las ligas"] = "Todas las ligas"
            
            for _, row in df[['league_name', 'country_name']].drop_duplicates().iterrows():
                liga = row['league_name']
                pais = row['country_name']
                display_text = f"{pais} - {liga}"
                ligas_dict[display_text] = liga
            
            # Solo "Todas las ligas" + opciones ordenadas
            ligas_display = ["Todas las ligas"] + sorted([k for k in ligas_dict.keys() if k != "Todas las ligas"])
            
            liga_display = st.selectbox(
                "🏆 Liga",
                ligas_display,
                index=0,
                key="liga_ranking"
            )
            liga_seleccionada = ligas_dict[liga_display]
    
    # Segundo: Filtro por Equipo (depende de la liga seleccionada)
    with col1:
        # Filtro por equipo: "Equipo - País"
        if 'team_long_name' in df.columns and 'country_name' in df.columns:
            # Si hay liga seleccionada, filtrar equipos por esa liga
            if liga_seleccionada != "Todas las ligas":
                df_equipos = df[df['league_name'] == liga_seleccionada]
            else:
                df_equipos = df
            
            # Crear diccionario con formato "Equipo - País" -> nombre real equipo
            equipos_dict = {}
            equipos_dict["Todos los equipos"] = "Todos los equipos"
            
            for _, row in df_equipos[['team_long_name', 'country_name']].drop_duplicates().iterrows():
                equipo = row['team_long_name']
                pais = row['country_name']
                display_text = f"{equipo} - {pais}"
                equipos_dict[display_text] = equipo
            
            # Solo "Todos los equipos" + opciones ordenadas
            equipos_display = ["Todos los equipos"] + sorted([k for k in equipos_dict.keys() if k != "Todos los equipos"])
            
            equipo_display = st.selectbox(
                "⚽ Equipo",
                equipos_display,
                index=0,
                key="equipo_ranking"
            )
            equipo_seleccionado = equipos_dict[equipo_display]
    
    # Aplicar filtros al DataFrame
    df_filtrado = df.copy()
    
    if liga_seleccionada != "Todas las ligas":
        df_filtrado = df_filtrado[df_filtrado['league_name'] == liga_seleccionada]
    
    if equipo_seleccionado != "Todos los equipos":
        df_filtrado = df_filtrado[df_filtrado['team_long_name'] == equipo_seleccionado]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # TABS para categorías (como antes)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⭐ Overall", 
        "⚡ Velocidad", 
        "🎯 Finalización", 
        "⚽ Pases", 
        "🕺 Regate",
        "🧤 Porteros"
    ])
    
    # Función helper para mostrar ranking paginado
    def display_ranking(df_data, stat_column, tab_key):
        if stat_column not in df_data.columns:
            st.warning(f"No hay datos disponibles para esta categoría.")
            return
        
        # Filtro especial para porteros
        if stat_column == 'gk_reflexes':
            df_data = df_data[df_data['gk_reflexes'] > 10]
        
        # Ordenar y obtener top jugadores
        df_top = df_data.nlargest(100, stat_column)[['player_name', stat_column, 'team_long_name', 'league_name', 'country_name']].reset_index(drop=True)
        
        if len(df_top) == 0:
            st.warning("No hay jugadores que cumplan con los filtros seleccionados.")
            return
        
        # Paginación
        items_por_pagina = 20
        total_paginas = (len(df_top) - 1) // items_por_pagina + 1
        
        # Control de paginación por tab
        pagina_key = f'pagina_{tab_key}'
        if pagina_key not in st.session_state:
            st.session_state[pagina_key] = 1
        
        # Resetear página si cambian filtros
        filtros_key = f"{tab_key}_{liga_seleccionada}_{equipo_seleccionado}"
        filtros_prev_key = f'filtros_{tab_key}'
        if filtros_prev_key not in st.session_state or st.session_state[filtros_prev_key] != filtros_key:
            st.session_state[pagina_key] = 1
            st.session_state[filtros_prev_key] = filtros_key
        
        pagina_actual = st.session_state[pagina_key]
        
        # Botones de paginación
        col_prev, col_info, col_next = st.columns([5, 20, 5])
        
        with col_prev:
            if st.button("⬅️ Anterior", key=f"prev_{tab_key}", disabled=(pagina_actual == 1)):
                st.session_state[pagina_key] -= 1
                st.rerun()
        
        with col_info:
            st.markdown(f"<div style='text-align: center; padding-top: 5px;'><b>Página {pagina_actual} de {total_paginas}</b> | Total: {len(df_top)} jugadores</div>", unsafe_allow_html=True)
        
        with col_next:
            if st.button("Siguiente ➡️", key=f"next_{tab_key}", disabled=(pagina_actual == total_paginas)):
                st.session_state[pagina_key] += 1
                st.rerun()
        
        # Calcular índices para la página actual
        inicio = (pagina_actual - 1) * items_por_pagina
        fin = min(inicio + items_por_pagina, len(df_top))
        
        df_pagina = df_top.iloc[inicio:fin]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Centrar el contenido usando columnas - tabla más estrecha
        col_izq, col_centro, col_der = st.columns([1, 2, 1])
        
        with col_centro:
            # Mostrar jugadores de la página actual
            for idx, (i, player) in enumerate(df_pagina.iterrows(), inicio + 1):
                # Color diferente para top 3
                if idx == 1:
                    medal = "🥇"
                    color = "#FFD700"  # Oro
                elif idx == 2:
                    medal = "🥈"
                    color = "#C0C0C0"  # Plata
                elif idx == 3:
                    medal = "🥉"
                    color = "#CD7F32"  # Bronce
                else:
                    medal = f"{idx}."
                    color = "#E8E8E8"  # Gris claro
                
                # Crear columnas para el diseño (más compacto)
                col1, col2, col3 = st.columns([0.4, 3.5, 0.8])
                
                with col1:
                    st.markdown(f"<div style='font-size: 24px; font-weight: bold; padding-top: 3px;'>{medal}</div>", unsafe_allow_html=True)
                
                with col2:
                    # Nombre del jugador e info en la misma línea
                    equipo = player['team_long_name'] if pd.notna(player['team_long_name']) else 'N/A'
                    liga = player['league_name'] if pd.notna(player['league_name']) else 'N/A'
                    pais = player['country_name'] if pd.notna(player['country_name']) else 'N/A'
                    
                    st.markdown(
                        f"<div style='padding-top: 5px;'>"
                        f"<span style='font-size: 18px; font-weight: bold;'>{player['player_name']}</span>"
                        f"<span style='font-size: 16px; color: #999999 !important; margin-left: 12px;'>⚽ {equipo} | 🏆 {liga} - {pais}</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                
                with col3:
                    st.markdown(f"<div style='font-size: 26px; font-weight: bold; text-align: right; padding-top: 3px;'>{player[stat_column]:.0f}</div>", unsafe_allow_html=True)
                
                st.markdown(f"<hr style='margin: 6px 0; border: 0; border-top: 1px solid {color};'>", unsafe_allow_html=True)
        
        # Botones de paginación al final también
        st.markdown("<br>", unsafe_allow_html=True)
        col_prev2, col_info2, col_next2 = st.columns([1, 5, 10])
        
        with col_prev2:
            if st.button("⬅️ Anterior ", key=f"prev2_{tab_key}", disabled=(pagina_actual == 1)):
                st.session_state[pagina_key] -= 1
                st.rerun()
        
        with col_info2:
            st.markdown(f"<div style='text-align: center; padding-top: 5px;'><b>Página {pagina_actual} de {total_paginas}</b></div>", unsafe_allow_html=True)
        
        with col_next2:
            if st.button("Siguiente ➡️ ", key=f"next2_{tab_key}", disabled=(pagina_actual == total_paginas)):
                st.session_state[pagina_key] += 1
                st.rerun()
    
    # TAB 1: TOP Overall Rating
    with tab1:
        display_ranking(df_filtrado, 'overall_rating', 'overall')
    
    # TAB 2: TOP Velocidad
    with tab2:
        display_ranking(df_filtrado, 'sprint_speed', 'speed')
    
    # TAB 3: TOP Finalización
    with tab3:
        display_ranking(df_filtrado, 'finishing', 'finishing')
    
    # TAB 4: TOP Pases
    with tab4:
        display_ranking(df_filtrado, 'short_passing', 'passing')
    
    # TAB 5: TOP Regate
    with tab5:
        display_ranking(df_filtrado, 'dribbling', 'dribbling')
    
    # TAB 6: TOP Porteros
    with tab6:
        display_ranking(df_filtrado, 'gk_reflexes', 'gk')
