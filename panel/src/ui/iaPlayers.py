"""
IA PLAYERS - Generador de Escenas Personalizadas con IA
Autor: Sistema Soccer Analytics
Descripción: Crea escenas únicas combinando hasta 3 jugadores con descripciones personalizadas
"""

import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class SceneImageGenerator:
    """Generador de escenas con IA usando múltiples jugadores"""
    
    def __init__(self):
        """Inicializa el generador con la API key de Hugging Face"""
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.model_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        self.fallback_models = [
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        ]
    
    def _generar_imagen(self, prompt, modelo_url=None, timeout=60):
        """
        Genera una imagen usando la API de Hugging Face con sistema de fallback
        
        Args:
            prompt: Descripción de la imagen a generar
            modelo_url: URL del modelo a usar (opcional, usa el principal por defecto)
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            Image object de PIL o None si falla
        """
        if not self.api_key:
            st.error("❌ API Key de Hugging Face no configurada")
            return None
        
        # Usar modelo principal o el especificado
        url_to_use = modelo_url if modelo_url else self.model_url
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 4,
                "guidance_scale": 3.5,
                "width": 768,
                "height": 768
            }
        }
        
        try:
            response = requests.post(url_to_use, headers=headers, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            elif response.status_code == 503:
                st.warning(f"⏳ Modelo cargándose... Reintentando en 20 segundos...")
                import time
                time.sleep(20)
                return self._generar_imagen(prompt, url_to_use, timeout)
            elif response.status_code == 404:
                st.error(f"❌ Modelo no encontrado o requiere aceptar licencia")
                return None
            elif response.status_code == 401:
                st.error(f"❌ Error de autenticación. Verifica tu API Key")
                return None
            else:
                st.error(f"❌ Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout: La generación tardó demasiado")
            return None
        except Exception as e:
            st.error(f"❌ Error al generar imagen: {str(e)}")
            return None
    
    def generar_escena_personalizada(self, jugadores, descripcion_escena):
        """
        Genera una escena personalizada con múltiples jugadores
        
        Args:
            jugadores: Lista de nombres de jugadores (1-3)
            descripcion_escena: Descripción personalizada de la escena (puede estar en español)
            
        Returns:
            tuple: (Image object de PIL o None si falla, prompt generado)
        """
        if not jugadores:
            st.error("❌ Debes seleccionar al menos un jugador")
            return None, None
        
        # Mapeo de descripciones en español a inglés para mejor calidad de generación
        traducciones = {
            "Los jugadores están jugando al fútbol en una hermosa playa al atardecer, divirtiéndose y riendo juntos": 
                "The players are playing soccer on a beautiful beach at sunset, having fun and laughing together",
            "Dos legendarios jugadores de fútbol jugando al ajedrez en una sala elegante, concentrados y estratégicos, competencia amistosa": 
                "Two legendary soccer players playing chess in a elegant room, focused and strategic, friendly competition",
            "Jugadores de fútbol entrenando juntos en un gimnasio moderno, motivándose mutuamente, sesión de entrenamiento intenso": 
                "Soccer players training together in a modern gym, motivating each other, intense workout session",
            "Jugadores celebrando una victoria de campeonato con fuegos artificiales en el fondo, pura alegría y emoción": 
                "Players celebrating a championship victory with fireworks in the background, pure joy and emotion",
            "Estrellas del fútbol disfrutando de una barbacoa relajada en un jardín, ropa casual, ambiente amigable": 
                "Soccer stars having a relaxed barbecue in a backyard, casual clothes, friendly atmosphere"
        }
        
        # Traducir a inglés si está en el diccionario, sino usar la descripción original
        descripcion_en_ingles = traducciones.get(descripcion_escena, descripcion_escena)
        
        # Construir prompt optimizado con especificaciones técnicas
        jugadores_str = ", ".join(jugadores)
        
        # Prompt mejorado con énfasis en que aparezcan los jugadores específicos
        prompt = f"""Professional high-quality sports photography: {descripcion_en_ingles}
The scene MUST feature these specific soccer players: {jugadores_str}.
Make sure all selected players are clearly visible and recognizable in the image.
Cinematic lighting, photorealistic, ultra detailed, 8K resolution, dynamic composition, dramatic atmosphere.
Professional sports photography style, natural poses, authentic soccer environment.
Sharp focus on the players, vibrant colors, perfect composition."""
        
        # Intentar con modelo principal
        imagen = self._generar_imagen(prompt)
        
        # Si falla, intentar con modelos de respaldo
        if imagen is None:
            for idx, fallback_url in enumerate(self.fallback_models):
                st.info(f"🔄 Intentando con modelo alternativo {idx + 1}...")
                imagen = self._generar_imagen(prompt, fallback_url)
                if imagen:
                    break
        
        return imagen, prompt


def render_top_players_page():
    """Función principal para renderizar la página de IA Players"""
    
    st.title("🤖 IA Players - Generador de Escenas con IA")
    st.markdown("---")
    
    # Verificar que existan datos
    if 'df' not in st.session_state or st.session_state.df is None:
        st.error("❌ No hay datos cargados. Por favor, vuelve a la página de inicio.")
        return
    
    df = st.session_state.df
    
    
    # Obtener top 10 por overall rating
    top_10 = df.nlargest(10, 'overall_rating')[['player_name', 'overall_rating']].copy()
    top_10.index = range(1, 11)
    top_10.columns = ['Jugador', 'Rating']

    st.markdown("---")
    
    # ========================================
    # SECCIÓN 2: GENERADOR DE ESCENAS CON IA
    # ========================================
    st.header("🎨 Generador de Escenas Personalizadas")
    
    # Información sobre la tecnología utilizada
    with st.expander("ℹ️ Sobre la tecnología de IA", expanded=False):
        st.markdown("""
        ### 🤖 Hugging Face - Plataforma de IA
        
        Esta funcionalidad utiliza **Hugging Face**, la plataforma líder en inteligencia artificial y machine learning.
        Hugging Face aloja miles de modelos de IA de código abierto y facilita su integración en aplicaciones.
        
        ### ⚡ Modelo: FLUX.1-schnell
        
        **FLUX.1-schnell** es un modelo de generación de imágenes de última generación desarrollado por Black Forest Labs.
        
        **Características principales:**
        - 🚀 **Ultra-rápido**: Genera imágenes en 10-30 segundos
        - 🎨 **Alta calidad**: Resolución profesional y detalles fotorrealistas
        - ✅ **Código abierto**: Disponible gratuitamente para uso general
        - 🎯 **Especializado**: Optimizado para fotografía realista y escenas dinámicas
        - 📊 **Eficiente**: Solo requiere 4 pasos de inferencia (vs 20-50 de otros modelos)
        
        **Alternativas disponibles:**
        - Stable Diffusion XL Base (modelo de respaldo)
        - FLUX.1-dev (modelo de respaldo con más detalle)
        
        *Si necesitas tu propia API key gratuita: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)*
        """)
    
    # Inicializar generador de imágenes
    generator = SceneImageGenerator()
    
    # Comprobar si hay API key configurada
    if not generator.api_key:
        st.error("""
        ❌ **API Key no configurada**
        
        Para usar esta funcionalidad:
        1. Ve a https://huggingface.co/settings/tokens
        2. Crea un token de acceso (Read)
        3. Añádelo al archivo `.env` en la raíz del proyecto:
           ```
           HUGGINGFACE_API_KEY=hf_tu_token_aqui
           ```
        4. Reinicia la aplicación
        """)
        return
    
    st.success("✅ API Key configurada correctamente")
    
    # PASO 1: Selección de jugadores (máximo 3)
    st.subheader("1️⃣ Selecciona jugadores (máximo 3)")
    
    # Obtener top 100 jugadores para el selector
    top_100_players = df.nlargest(100, 'overall_rating')['player_name'].tolist()
    
    jugadores_seleccionados = st.multiselect(
        "Arrastra y selecciona entre 1 y 3 jugadores:",
        options=top_100_players,
        max_selections=3,
        placeholder="Selecciona jugadores...",
        help="Puedes seleccionar de 1 a 3 jugadores para tu escena"
    )
    
    # PASO 2: Descripción de la escena
    st.subheader("2️⃣ Describe la escena que quieres crear")
    
    # Opciones predefinidas de escenas en castellano
    escenas_predefinidas = [
        "Los jugadores están jugando al fútbol en una hermosa playa al atardecer, divirtiéndose y riendo juntos",
        "Dos legendarios jugadores de fútbol jugando al ajedrez en una sala elegante, concentrados y estratégicos, competencia amistosa",
        "Jugadores de fútbol entrenando juntos en un gimnasio moderno, motivándose mutuamente, sesión de entrenamiento intenso",
        "Jugadores celebrando una victoria de campeonato con fuegos artificiales en el fondo, pura alegría y emoción",
        "Estrellas del fútbol disfrutando de una barbacoa relajada en un jardín, ropa casual, ambiente amigable"
    ]
    
    descripcion_escena = st.selectbox(
        "Selecciona una escena predefinida:",
        options=escenas_predefinidas,
        help="Elige una de las escenas prediseñadas para generar tu imagen"
    )
    
    # PASO 3: Botón de generación
    st.markdown("###")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        generar_escena = st.button(
            "🎨 Generar Escena con IA",
            type="primary",
            use_container_width=True,
            disabled=not jugadores_seleccionados
        )
    
    if not jugadores_seleccionados:
        st.info("👆 Selecciona al menos 1 jugador para continuar")
    
    # PASO 4: Generación y visualización
    if generar_escena and jugadores_seleccionados:
        
        # Mostrar información de lo que se está generando
        jugadores_str = ", ".join(jugadores_seleccionados)
        st.info(f"🎬 Generando escena con: **{jugadores_str}**")
        
        # Generar imagen con spinner
        with st.spinner(f"🎨 Generando escena... Esto puede tardar 10-30 segundos..."):
            imagen, prompt_usado = generator.generar_escena_personalizada(jugadores_seleccionados, descripcion_escena)
        
        # PASO 5: Mostrar resultado y descarga
        if imagen:
            st.success("✅ ¡Escena generada con éxito!")
            
            # Guardar en session_state para persistencia
            st.session_state.ultima_escena_generada = imagen
            st.session_state.ultimos_jugadores_escena = jugadores_seleccionados
            st.session_state.ultima_descripcion_escena = descripcion_escena
            st.session_state.ultimo_prompt_usado = prompt_usado
            
            # Mostrar imagen en tamaño reducido (centrada y más pequeña en pantalla)
            col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
            
            with col_img2:
                st.image(imagen, caption=f"Escena generada: {jugadores_str}", use_container_width=True)
            
            # Mostrar prompt usado (para debugging)
            with st.expander("🔍 Ver prompt enviado a la IA"):
                st.code(prompt_usado, language="text")
                st.info("💡 El modelo de IA genera imágenes genéricas basadas en el prompt, no puede crear caras reales de personas específicas por cuestiones éticas y técnicas.")
            
            # Preparar archivo para descarga
            buffer = BytesIO()
            imagen.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Crear nombre de archivo
            jugadores_filename = "_".join([j.replace(" ", "_") for j in jugadores_seleccionados])
            filename = f"escena_ia_{jugadores_filename}.png"
            
            # Botón de descarga centrado
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            
            with col_dl2:
                st.download_button(
                    label="💾 Descargar Imagen",
                    data=buffer,
                    file_name=filename,
                    mime="image/png",
                    use_container_width=True
                )
            
            # Mostrar detalles
            with st.expander("📋 Detalles de la generación"):
                st.markdown(f"""
                **Jugadores incluidos:** {jugadores_str}
                
                **Descripción:** {descripcion_escena}
                
                **Modelo IA:** FLUX.1-schnell (black-forest-labs)
                
                **Resolución:** 768x768 pixels
                
                **Configuración técnica:**
                - Pasos de inferencia: 4
                - Guidance scale: 3.5
                - Estilo: Fotografía profesional fotorrealista
                """)
    
    # Mostrar última escena generada (persistencia entre interacciones)
    if 'ultima_escena_generada' in st.session_state and not generar_escena:
        st.markdown("---")
        st.markdown("### 🖼️ Última escena generada:")
        
        jugadores_previos = ", ".join(st.session_state.ultimos_jugadores_escena)
        
        # Mostrar imagen en tamaño reducido (centrada)
        col_prev1, col_prev2, col_prev3 = st.columns([1, 2, 1])
        
        with col_prev2:
            st.image(
                st.session_state.ultima_escena_generada,
                caption=f"Escena con: {jugadores_previos}",
                use_container_width=True
            )
        
        # Mostrar prompt usado (si existe)
        if 'ultimo_prompt_usado' in st.session_state:
            with st.expander("🔍 Ver prompt enviado a la IA"):
                st.code(st.session_state.ultimo_prompt_usado, language="text")
                st.info("💡 El modelo de IA genera imágenes genéricas basadas en el prompt, no puede crear caras reales de personas específicas por cuestiones éticas y técnicas.")
        
        # Botón de descarga persistente
        buffer_persistente = BytesIO()
        st.session_state.ultima_escena_generada.save(buffer_persistente, format='PNG')
        buffer_persistente.seek(0)
        
        jugadores_filename_prev = "_".join([j.replace(" ", "_") for j in st.session_state.ultimos_jugadores_escena])
        filename_prev = f"escena_ia_{jugadores_filename_prev}.png"
        
        col_persist1, col_persist2, col_persist3 = st.columns([1, 2, 1])
        
        with col_persist2:
            st.download_button(
                label="💾 Descargar Última Escena",
                data=buffer_persistente,
                file_name=filename_prev,
                mime="image/png",
                use_container_width=True,
                key="download_persistent"
            )
        
        with st.expander("📋 Detalles de esta escena"):
            st.markdown(f"""
            **Jugadores:** {jugadores_previos}
            
            **Descripción:** {st.session_state.ultima_descripcion_escena}
            """)
    
    st.markdown("---")
    st.markdown("*Escenas generadas con IA usando FLUX.1-schnell | Datos del dataset FIFA*")
