import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def get_team_logo_url(team_name):
    """
    Obtiene la URL del escudo de un equipo de fútbol desde Wikipedia.
    Solo incluye URLs verificadas que funcionan correctamente.
    """
    # Diccionario de URLs verificadas de escudos (solo las que funcionan)
    known_logos = {
        # España - La Liga
        'FC Barcelona': 'https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg',
        'Real Madrid': 'https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg',
        'Atlético Madrid': 'https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg',
        'Valencia': 'https://upload.wikimedia.org/wikipedia/en/c/ce/Valenciacf.svg',
        'Sevilla': 'https://upload.wikimedia.org/wikipedia/en/3/3b/Sevilla_FC_logo.svg',
        'Athletic Bilbao': 'https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg',
        'Villarreal': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Villarreal_CF_logo.svg',
        
        # Inglaterra - Premier League
        'Manchester United': 'https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg',
        'Manchester City': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg',
        'Chelsea': 'https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg',
        'Arsenal': 'https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg',
        'Liverpool': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg',
        'Tottenham': 'https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg',
        
        # Alemania - Bundesliga
        'Bayern Munich': 'https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg',
        'Borussia Dortmund': 'https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg',
        
        # Italia - Serie A
        'Juventus': 'https://upload.wikimedia.org/wikipedia/commons/a/a8/Juventus_FC_-_pictogram_black_%28Italy%2C_2017%29.svg',
        'AC Milan': 'https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg',
        'Inter Milan': 'https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg',
        
        # Francia - Ligue 1
        'Paris Saint-Germain': 'https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg',
    }
    
    # Buscar en el diccionario (búsqueda flexible)
    team_lower = team_name.lower()
    for key, url in known_logos.items():
        if key.lower() in team_lower or team_lower in key.lower():
            return url
    
    # URL genérica de respaldo (escudo neutral de fútbol)
    return 'https://upload.wikimedia.org/wikipedia/commons/6/6e/Football_%28soccer_ball%29.svg'

def render_teams_page(df):
    """
    Página de análisis por equipo con visualizaciones mejoradas y comparación.
    """
    
    st.markdown("## 👕 Análisis por Equipo")
    st.markdown("Explora en detalle la composición, fortalezas y debilidades de cada equipo de la temporada 2015-2016.")
    
    st.markdown("---")
    
    # ========== SECCIÓN 1: SELECTOR DE EQUIPO ==========
    st.markdown("### 🎯 Selecciona un Equipo")
    
    if 'team_long_name' in df.columns:
        # Crear lista de equipos con liga y país
        equipos_con_info = df[['team_long_name', 'league_name', 'country_name']].drop_duplicates()
        equipos_con_info['display_name'] = equipos_con_info['team_long_name'] + ' (' + equipos_con_info['league_name'] + ')'
        equipos_con_info = equipos_con_info.sort_values('team_long_name')
        
        # Buscar FC Barcelona como default
        lista_equipos = equipos_con_info['display_name'].tolist()
        default_index = 0
        for idx, nombre in enumerate(lista_equipos):
            if 'FC Barcelona' in nombre or 'Barcelona' in nombre:
                default_index = idx
                break
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            equipo_display = st.selectbox(
                "🏟️ Busca tu equipo:",
                options=lista_equipos,
                index=default_index,
                key='equipo_selector'
            )
            
            # Extraer nombre del equipo
            equipo_seleccionado = equipos_con_info[equipos_con_info['display_name'] == equipo_display]['team_long_name'].iloc[0]
        
        if equipo_seleccionado:
            df_equipo = df[df['team_long_name'] == equipo_seleccionado]
            liga_equipo = df_equipo['league_name'].iloc[0]
            pais_equipo = df_equipo['country_name'].iloc[0]
            
            with col2:
                st.metric("🌍 País", pais_equipo)
            
            with col3:
                st.metric("🏆 Liga", liga_equipo)
            
            # Aplicar fondo con escudo del equipo
            logo_url = get_team_logo_url(equipo_seleccionado)
            st.markdown(
                f"""
                <style>
                /* Fondo con escudo del equipo */
                .stApp {{
                    background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), 
                                url("{logo_url}") !important;
                    background-size: 400px 400px !important;
                    background-position: center center !important;
                    background-repeat: no-repeat !important;
                    background-attachment: fixed !important;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            
            # ========== SECCIÓN 2: MÉTRICAS GENERALES DEL EQUIPO ==========
            st.markdown(f"### 📊 Estadísticas Generales: {equipo_seleccionado}")
            st.markdown("Aquí puedes ver un resumen del nivel global del equipo y sus jugadores más destacados.")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                num_jugadores = len(df_equipo)
                st.metric("👥 Plantilla", num_jugadores)
            
            with col2:
                rating_medio = df_equipo['overall_rating'].mean()
                st.metric("⭐ Rating Medio", f"{rating_medio:.1f}")
            
            with col3:
                mejor_jugador = df_equipo.nlargest(1, 'overall_rating')['player_name'].iloc[0]
                mejor_rating = df_equipo['overall_rating'].max()
                st.metric("🌟 Mejor Jugador", mejor_jugador)
                st.caption(f"Rating: {mejor_rating}")
            
            with col4:
                elite_count = (df_equipo['overall_rating'] >= 80).sum()
                elite_pct = (elite_count / num_jugadores) * 100
                st.metric("💎 Jugadores Elite", elite_count)
                st.caption(f"{elite_pct:.1f}% del equipo")
            
            with col5:
                edad_media = (pd.Timestamp('2016-12-31') - pd.to_datetime(df_equipo['birthday'])).dt.days.mean() / 365.25
                st.metric("📅 Edad Media", f"{edad_media:.1f}")
            
            st.markdown("---")
            
            # ========== SECCIÓN 3: ANÁLISIS POR PIE PREFERIDO ==========
            st.markdown("### 🦶 Análisis: ¿Zurdos vs Diestros?")
            st.markdown("Descubre si existe una diferencia de rendimiento o especialización entre los jugadores según su pie preferido.")
            
            if 'preferred_foot' in df.columns:
                # Filtrar solo zurdos y diestros (sin NaN)
                df_pie = df_equipo[df_equipo['preferred_foot'].isin(['left', 'right'])].copy()
                df_pie['Pie Preferido'] = df_pie['preferred_foot'].map({'right': 'Diestro', 'left': 'Zurdo'})
                
                # Comparar atributos entre zurdos y diestros
                atributos_comp = ['ball_control', 'dribbling', 'finishing', 'short_passing', 
                                 'shot_power', 'acceleration', 'sprint_speed', 'stamina']
                atributos_comp_disp = [attr for attr in atributos_comp if attr in df.columns]
                
                if atributos_comp_disp and len(df_pie) > 0:
                    # Calcular promedios por pie
                    comparacion_pie = df_pie.groupby('Pie Preferido')[atributos_comp_disp].mean()
                    
                    # Crear DataFrame para visualización
                    nombres_atributos = {
                        'ball_control': 'Control',
                        'dribbling': 'Regate',
                        'finishing': 'Finalización',
                        'short_passing': 'Pase',
                        'shot_power': 'Potencia',
                        'acceleration': 'Aceleración',
                        'sprint_speed': 'Velocidad',
                        'stamina': 'Resistencia'
                    }
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Gráfico de barras agrupadas
                        df_plot = comparacion_pie.T.reset_index()
                        df_plot.columns = ['Atributo'] + list(comparacion_pie.index)
                        df_plot['Atributo'] = df_plot['Atributo'].map(nombres_atributos)
                        
                        fig_pie = go.Figure()
                        
                        if 'Diestro' in df_plot.columns:
                            fig_pie.add_trace(go.Bar(
                                name='Diestros',
                                x=df_plot['Atributo'],
                                y=df_plot['Diestro'],
                                marker_color='#3498db',
                                text=df_plot['Diestro'].round(1),
                                textposition='outside'
                            ))
                        
                        if 'Zurdo' in df_plot.columns:
                            fig_pie.add_trace(go.Bar(
                                name='Zurdos',
                                x=df_plot['Atributo'],
                                y=df_plot['Zurdo'],
                                marker_color='#e74c3c',
                                text=df_plot['Zurdo'].round(1),
                                textposition='outside'
                            ))
                        
                        fig_pie.update_layout(
                            title='Comparación de Atributos: Diestros vs Zurdos',
                            barmode='group',
                            height=400,
                            yaxis_title='Nivel del Atributo',
                            xaxis_title='',
                            yaxis=dict(range=[0, 100])
                        )
                        
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### 💡 Conclusiones")
                        
                        # Contar jugadores
                        num_diestros = len(df_pie[df_pie['Pie Preferido'] == 'Diestro'])
                        num_zurdos = len(df_pie[df_pie['Pie Preferido'] == 'Zurdo'])
                        
                        st.markdown(f"**👥 Plantilla:**")
                        st.caption(f"Diestros: {num_diestros} | Zurdos: {num_zurdos}")
                        
                        if 'Diestro' in comparacion_pie.index and 'Zurdo' in comparacion_pie.index:
                            # Calcular diferencias
                            diferencias = comparacion_pie.loc['Zurdo'] - comparacion_pie.loc['Diestro']
                            
                            # Encontrar mayores fortalezas de zurdos
                            mejor_zurdo = diferencias.nlargest(2)
                            # Encontrar mayores fortalezas de diestros
                            mejor_diestro = diferencias.nsmallest(2)
                            
                            st.markdown("**🔴 Zurdos destacan en:**")
                            for attr, diff in mejor_zurdo.items():
                                if diff > 0.5:
                                    st.caption(f"• {nombres_atributos.get(attr, attr)} (+{diff:.1f})")
                            
                            st.markdown("**🔵 Diestros destacan en:**")
                            for attr, diff in mejor_diestro.items():
                                if diff < -0.5:
                                    st.caption(f"• {nombres_atributos.get(attr, attr)} ({diff:.1f})")
                            
                            # Rating promedio
                            rating_diestro = df_pie[df_pie['Pie Preferido'] == 'Diestro']['overall_rating'].mean()
                            rating_zurdo = df_pie[df_pie['Pie Preferido'] == 'Zurdo']['overall_rating'].mean()
                            
                            st.markdown(f"**⭐ Rating Promedio:**")
                            st.caption(f"Diestros: {rating_diestro:.1f} | Zurdos: {rating_zurdo:.1f}")
            
            st.markdown("---")
            
            # ========== SECCIÓN 4: SCATTER 3D - ATRIBUTOS FÍSICOS (MEJORADO) ==========
            st.markdown("### 🚀 Análisis 3D de Atributos Físicos")
            st.markdown("Explora la relación entre agilidad, velocidad y aceleración de cada jugador. **Bolas rojas y grandes = jugadores élite. Bolas amarillas y pequeñas = jugadores con menor rendimiento.**")
            
            if all(attr in df.columns for attr in ['agility', 'sprint_speed', 'acceleration', 'overall_rating']):
                # Escala personalizada: amarillo claro para bajos, rojo para altos
                fig_3d = px.scatter_3d(
                    df_equipo,
                    x='agility',
                    y='sprint_speed',
                    z='acceleration',
                    color='overall_rating',
                    size='overall_rating',
                    hover_name='player_name',
                    color_continuous_scale=[[0, '#ffffcc'], [0.5, '#ff7f00'], [1, '#cc0000']],  # Amarillo claro -> Naranja -> Rojo
                    title=f'Atributos Físicos 3D: {equipo_seleccionado}',
                    labels={
                        'agility': 'Agilidad',
                        'sprint_speed': 'Velocidad',
                        'acceleration': 'Aceleración',
                        'overall_rating': 'Rating'
                    }
                )
                
                # Actualizar el estilo del gráfico con cuadrícula azul claro
                fig_3d.update_layout(
                    height=600,
                    scene=dict(
                        xaxis=dict(
                            backgroundcolor="rgb(230, 240, 250)",
                            gridcolor="rgb(173, 216, 230)",
                            showbackground=True,
                            zerolinecolor="rgb(173, 216, 230)"
                        ),
                        yaxis=dict(
                            backgroundcolor="rgb(230, 240, 250)",
                            gridcolor="rgb(173, 216, 230)",
                            showbackground=True,
                            zerolinecolor="rgb(173, 216, 230)"
                        ),
                        zaxis=dict(
                            backgroundcolor="rgb(230, 240, 250)",
                            gridcolor="rgb(173, 216, 230)",
                            showbackground=True,
                            zerolinecolor="rgb(173, 216, 230)"
                        )
                    )
                )
                st.plotly_chart(fig_3d, use_container_width=True)
            
            st.markdown("---")
            
            # ========== SECCIÓN 5: HEATMAP - PERFIL DE JUGADORES ==========
            st.markdown("### 🔥 Mapa de Calor: Perfil de Atributos por Jugador")
            st.markdown("Visualiza las fortalezas y debilidades de cada jugador del equipo. **Verde = excelente, Amarillo = promedio, Rojo = débil.**")
            
            # Atributos clave para analizar
            atributos_analisis = ['ball_control', 'dribbling', 'finishing', 'short_passing', 
                                 'shot_power', 'acceleration', 'sprint_speed']
            atributos_disponibles = [attr for attr in atributos_analisis if attr in df.columns]
            
            if atributos_disponibles and len(atributos_disponibles) > 1:
                # Nombres en español
                nombres_es = {
                    'ball_control': 'Control',
                    'dribbling': 'Regate',
                    'finishing': 'Finalización',
                    'short_passing': 'Pase',
                    'shot_power': 'Potencia',
                    'acceleration': 'Aceleración',
                    'sprint_speed': 'Velocidad'
                }
                
                # Seleccionar top 15 jugadores por rating
                df_top = df_equipo.nlargest(15, 'overall_rating').copy()
                
                # Crear matriz con jugadores en filas y atributos en columnas
                df_heatmap = df_top[['player_name'] + atributos_disponibles].set_index('player_name')
                df_heatmap.columns = [nombres_es.get(col, col) for col in df_heatmap.columns]
                
                # Crear heatmap
                fig_heatmap = px.imshow(
                    df_heatmap,
                    color_continuous_scale='RdYlGn',
                    aspect='auto',
                    title=f'Top 15 Jugadores - Perfil de Atributos: {equipo_seleccionado}',
                    zmin=0,
                    zmax=100,
                    text_auto='.0f',
                    labels=dict(x="Atributo", y="Jugador", color="Nivel")
                )
                
                fig_heatmap.update_layout(height=600)
                fig_heatmap.update_xaxes(side="top")
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            st.markdown("---")
            
            # ========== SECCIÓN 6: TOP Y BOTTOM JUGADORES ==========
            st.markdown("### ⭐ Mejores y Peores Jugadores del Equipo")
            st.markdown("Conoce a las estrellas y a los jugadores con menor rendimiento de la plantilla.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top 5 Mejores")
                top_5 = df_equipo.nlargest(5, 'overall_rating')[['player_name', 'overall_rating']]
                
                for idx, row in top_5.iterrows():
                    st.markdown(f"**{row['player_name']}** - Rating: {row['overall_rating']}")
            
            with col2:
                st.markdown("#### 📉 Top 5 Flojos")
                bottom_5 = df_equipo.nsmallest(5, 'overall_rating')[['player_name', 'overall_rating']]
                
                for idx, row in bottom_5.iterrows():
                    st.markdown(f"**{row['player_name']}** - Rating: {row['overall_rating']}")
            
            st.markdown("---")
            
            # ========== SECCIÓN 7: COMPARADOR DE EQUIPOS ==========
            st.markdown("### ⚔️ Comparador de Equipos")
            st.markdown("Compara tu equipo seleccionado con otro equipo para ver diferencias en nivel, composición y estadísticas clave.")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Selector del equipo a comparar
                equipos_comparar = [e for e in lista_equipos if equipos_con_info[equipos_con_info['display_name'] == e]['team_long_name'].iloc[0] != equipo_seleccionado]
                
                # Buscar Real Madrid como default
                default_comp_index = 0
                for idx, nombre in enumerate(equipos_comparar):
                    if 'Real Madrid' in nombre:
                        default_comp_index = idx
                        break
                
                equipo_comp_display = st.selectbox(
                    "🔎 Comparar con:",
                    options=equipos_comparar,
                    index=default_comp_index,
                    key='equipo_comparar'
                )
                
                equipo_comparar = equipos_con_info[equipos_con_info['display_name'] == equipo_comp_display]['team_long_name'].iloc[0]
            
            if equipo_comparar:
                df_comparar = df[df['team_long_name'] == equipo_comparar]
                
                # Métricas comparativas con nombres de equipos acortados
                equipo_1_corto = equipo_seleccionado.split()[0] if len(equipo_seleccionado) > 15 else equipo_seleccionado
                equipo_2_corto = equipo_comparar.split()[0] if len(equipo_comparar) > 15 else equipo_comparar
                
                st.markdown(f"#### 📊 Comparación de Rendimiento")
                st.markdown(f"**🔵 {equipo_seleccionado}** vs **🔴 {equipo_comparar}**")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    rating_1 = df_equipo['overall_rating'].mean()
                    rating_2 = df_comparar['overall_rating'].mean()
                    diff = rating_1 - rating_2
                    
                    if diff > 0:
                        ganador = f"✅ {equipo_1_corto}"
                        delta_label = f"+{diff:.1f}"
                    elif diff < 0:
                        ganador = f"✅ {equipo_2_corto}"
                        delta_label = f"{diff:.1f}"
                    else:
                        ganador = "⚖️ Empate"
                        delta_label = "0.0"
                    
                    st.metric("⭐ Rating Medio", f"{rating_1:.1f} vs {rating_2:.1f}", delta_label)
                    st.markdown(f"**{ganador}**")
                
                with col2:
                    plantilla_1 = len(df_equipo)
                    plantilla_2 = len(df_comparar)
                    diff_plant = plantilla_1 - plantilla_2
                    
                    if diff_plant > 0:
                        ganador = f"✅ {equipo_1_corto}"
                        delta_label = f"+{diff_plant}"
                    elif diff_plant < 0:
                        ganador = f"✅ {equipo_2_corto}"
                        delta_label = f"{diff_plant}"
                    else:
                        ganador = "⚖️ Empate"
                        delta_label = "0"
                    
                    st.metric("👥 Plantilla", f"{plantilla_1} vs {plantilla_2}", delta_label)
                    st.markdown(f"**{ganador}**")
                
                with col3:
                    elite_1 = (df_equipo['overall_rating'] >= 80).sum()
                    elite_2 = (df_comparar['overall_rating'] >= 80).sum()
                    diff_elite = elite_1 - elite_2
                    
                    if diff_elite > 0:
                        ganador = f"✅ {equipo_1_corto}"
                        delta_label = f"+{diff_elite}"
                    elif diff_elite < 0:
                        ganador = f"✅ {equipo_2_corto}"
                        delta_label = f"{diff_elite}"
                    else:
                        ganador = "⚖️ Empate"
                        delta_label = "0"
                    
                    st.metric("💎 Jugadores Elite", f"{elite_1} vs {elite_2}", delta_label)
                    st.markdown(f"**{ganador}**")
                
                with col4:
                    max_1 = df_equipo['overall_rating'].max()
                    max_2 = df_comparar['overall_rating'].max()
                    diff_max = max_1 - max_2
                    
                    if diff_max > 0:
                        ganador = f"✅ {equipo_1_corto}"
                        delta_label = f"+{diff_max:.0f}"
                    elif diff_max < 0:
                        ganador = f"✅ {equipo_2_corto}"
                        delta_label = f"{diff_max:.0f}"
                    else:
                        ganador = "⚖️ Empate"
                        delta_label = "0"
                    
                    st.metric("🌟 Rating Máximo", f"{max_1:.0f} vs {max_2:.0f}", delta_label)
                    st.markdown(f"**{ganador}**")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Radar comparativo
                st.markdown("#### 🎯 Comparación de Atributos")
                
                atributos_radar = ['ball_control', 'dribbling', 'finishing', 'short_passing', 
                                  'acceleration', 'sprint_speed', 'stamina', 'aggression']
                atributos_radar_disp = [attr for attr in atributos_radar if attr in df.columns]
                
                if atributos_radar_disp:
                    # Calcular promedios solo con jugadores que tienen 70+ en cada atributo
                    prom_1 = pd.Series(dtype=float)
                    prom_2 = pd.Series(dtype=float)
                    
                    for attr in atributos_radar_disp:
                        # Para equipo 1: solo promediar jugadores con 70+ en este atributo
                        jugadores_calificados_1 = df_equipo[df_equipo[attr] >= 70]
                        if len(jugadores_calificados_1) > 0:
                            prom_1[attr] = jugadores_calificados_1[attr].mean()
                        else:
                            prom_1[attr] = 0  # Si nadie llega a 70, poner 0
                        
                        # Para equipo 2: solo promediar jugadores con 70+ en este atributo
                        jugadores_calificados_2 = df_comparar[df_comparar[attr] >= 70]
                        if len(jugadores_calificados_2) > 0:
                            prom_2[attr] = jugadores_calificados_2[attr].mean()
                        else:
                            prom_2[attr] = 0  # Si nadie llega a 70, poner 0
                    
                    nombres_radar = {
                        'ball_control': 'Control',
                        'dribbling': 'Regate',
                        'finishing': 'Finalización',
                        'short_passing': 'Pase Corto',
                        'acceleration': 'Aceleración',
                        'sprint_speed': 'Velocidad',
                        'stamina': 'Resistencia',
                        'aggression': 'Agresividad'
                    }
                    
                    fig_radar_comp = go.Figure()
                    
                    # Equipo 1
                    fig_radar_comp.add_trace(go.Scatterpolar(
                        r=prom_1.values,
                        theta=[nombres_radar.get(attr, attr) for attr in atributos_radar_disp],
                        fill='toself',
                        name=equipo_seleccionado,
                        line=dict(color='#3498db', width=3),
                        fillcolor='rgba(52, 152, 219, 0.3)'
                    ))
                    
                    # Equipo 2
                    fig_radar_comp.add_trace(go.Scatterpolar(
                        r=prom_2.values,
                        theta=[nombres_radar.get(attr, attr) for attr in atributos_radar_disp],
                        fill='toself',
                        name=equipo_comparar,
                        line=dict(color='#e74c3c', width=3),
                        fillcolor='rgba(231, 76, 60, 0.3)'
                    ))
                    
                    fig_radar_comp.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[69, 91]
                            )
                        ),
                        showlegend=True,
                        height=500,
                        title=f"Comparación de Atributos Promedio"
                    )
                    
                    st.plotly_chart(fig_radar_comp, use_container_width=True)
                
                # Tabla comparativa detallada
                st.markdown("#### 📋 Tabla Comparativa de Atributos")
                
                if atributos_radar_disp:
                    comparacion_tabla = pd.DataFrame({
                        'Atributo': [nombres_radar.get(attr, attr) for attr in atributos_radar_disp],
                        equipo_seleccionado: prom_1.values.round(1),
                        equipo_comparar: prom_2.values.round(1)
                    })
                    
                    comparacion_tabla['Diferencia'] = (comparacion_tabla[equipo_seleccionado] - comparacion_tabla[equipo_comparar]).round(1)
                    comparacion_tabla['Ventaja'] = comparacion_tabla['Diferencia'].apply(
                        lambda x: '✅ ' + equipo_seleccionado if x > 0 else ('🔶 ' + equipo_comparar if x < 0 else '➖ Empate')
                    )
                    
                    st.dataframe(comparacion_tabla, use_container_width=True, hide_index=True)
