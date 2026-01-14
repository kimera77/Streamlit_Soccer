# 📚 RESUMEN COMPLETO - Implementación de IA Generativa en Proyecto Soccer

## 🎯 OBJETIVO PRINCIPAL

Implementar funcionalidad de **generación de imágenes con IA** (retratos de jugadores) usando la API gratuita de Hugging Face, manteniendo una arquitectura limpia donde la IA está **aislada en un nuevo archivo** sin "ensuciar" el código existente.

---

## 📋 TABLA DE CONTENIDOS

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Arquitectura del Proyecto](#2-arquitectura-del-proyecto)
3. [Paso a Paso de la Implementación](#3-paso-a-paso-de-la-implementación)
4. [Código Detallado](#4-código-detallado)
5. [Seguridad y Buenas Prácticas](#5-seguridad-y-buenas-prácticas)
6. [Solución de Problemas](#6-solución-de-problemas)
7. [Lecciones Aprendidas](#7-lecciones-aprendidas)

---

## 1. CONCEPTOS FUNDAMENTALES

### 1.1 ¿Qué es una API de Generación de Imágenes?

Una **API** (Application Programming Interface) es una forma de comunicación entre tu programa y un servicio externo. En este caso:

```
TU APP → Envía texto descriptivo → API HUGGING FACE → Procesa con IA → Devuelve imagen
```

**Analogía:** Es como llamar a un artista profesional por teléfono y pedirle que dibuje algo según tu descripción.

### 1.2 ¿Qué es Stable Diffusion?

**Stable Diffusion** es un modelo de IA entrenado con millones de imágenes que puede:
- Generar imágenes desde cero basándose en texto
- Crear arte, retratos, logos, paisajes, etc.
- Funciona "aprendiendo" patrones de las imágenes con las que fue entrenado

**Versión usada:** `stable-diffusion-2-1` (versión 2.1, gratuita y potente)

### 1.3 Variables de Entorno vs Constantes

Esta es una distinción **CRÍTICA** en programación profesional:

| Concepto | Qué es | Dónde va | ¿Se sube a GitHub? | Ejemplo |
|----------|--------|----------|-------------------|---------|
| **Variable de Entorno** | Secretos, credenciales | `.env` | ❌ NUNCA | `HUGGINGFACE_API_KEY=hf_abc123` |
| **Constante** | Configuración pública | `const.py` | ✅ SÍ | `API_URL = "https://..."` |

**¿Por qué separar?**
- Si subes tu token a GitHub → cualquiera puede usarlo y agotar tu cuota
- Las constantes (URLs, parámetros) pueden ser públicas
- Permite tener diferentes tokens en desarrollo y producción

### 1.4 Diferencia entre `const.py` y `.env`

```python
# ❌ MALO - Todo en const.py (expones tu token)
# const.py
API_KEY = "hf_mi_token_secreto_123456"  # ¡Peligro si subes a GitHub!
API_URL = "https://api.huggingface.co"

# ✅ BUENO - Separación de responsabilidades
# .env (NO se sube a GitHub)
HUGGINGFACE_API_KEY=hf_mi_token_secreto_123456

# const.py (SÍ se sube a GitHub)
API_URL = "https://api.huggingface.co"
ENV_HUGGINGFACE_KEY = "HUGGINGFACE_API_KEY"  # Nombre de la variable
```

---

## 2. ARQUITECTURA DEL PROYECTO

### 2.1 Estructura de Archivos

```
PROYECTO1_Soccer/
│
├── .env                              # 🔒 SECRETOS (token API)
├── .gitignore                        # 🛡️ Protege .env
├── test_huggingface_setup.py         # 🧪 Script de verificación
├── README_HUGGINGFACE.md             # 📖 Documentación
│
├── data.csv, datadata.csv, data/     # 📊 Datos del proyecto
│
└── panel/src/
    ├── app.py                        # 🚀 Aplicación principal
    │
    ├── utils/
    │   ├── const.py                  # ⚙️ Configuración pública (MODIFICADO)
    │   ├── config.py                 # Configuración general
    │   └── data_loader.py            # Carga de datos
    │
    └── ui/
        ├── home.py                   # Página inicio (SIN cambios)
        ├── players.py                # Análisis jugadores (SIN cambios)
        ├── teams.py                  # Análisis equipos (SIN cambios)
        ├── leagues.py                # Análisis ligas (SIN cambios)
        └── top_players.py            # ⭐ NUEVO - IA generativa
```

### 2.2 Flujo de Datos

```
1. Usuario abre app.py
   ↓
2. app.py ejecuta load_dotenv() → Carga .env
   ↓
3. Usuario navega a "⭐ Top Jugadores"
   ↓
4. Se importa top_players.py
   ↓
5. PlayerImageGenerator.__init__() busca API key
   - Prioridad 1: Streamlit secrets
   - Prioridad 2: Variables de entorno (os.getenv)
   - Prioridad 3: Archivo .env (ya cargado)
   ↓
6. Usuario selecciona jugador y presiona "Generar"
   ↓
7. Se construye prompt desde PROMPT_TEMPLATES
   ↓
8. Se envía POST request a Hugging Face API
   ↓
9. API devuelve bytes de imagen
   ↓
10. Se convierte a PIL.Image y se muestra
    ↓
11. Se guarda en st.session_state (persistencia)
    ↓
12. Usuario puede descargar la imagen
```

### 2.3 Principio de Diseño: Aislamiento

**Pregunta clave:** *"¿Por qué crear un archivo nuevo en vez de añadir la IA a `players.py`?"*

**Respuesta:**

1. **Separación de responsabilidades:**
   - `players.py` → Análisis estadístico
   - `top_players.py` → Rankings + IA generativa

2. **Evita "ensuciar" código existente:**
   - Si la IA da problemas → solo afecta a `top_players.py`
   - Los otros archivos siguen funcionando sin cambios

3. **Más fácil de mantener:**
   - Toda la lógica de IA está en un solo lugar
   - Puedes eliminar la funcionalidad borrando un archivo

4. **Testeo independiente:**
   - Puedes probar la IA sin afectar otros módulos

---

## 3. PASO A PASO DE LA IMPLEMENTACIÓN

### PASO 1: Crear archivo `.env`

**Qué hace:** Almacena el token de API de forma segura

**Ubicación:** Raíz del proyecto (`PROYECTO1_Soccer/.env`)

**Contenido:**
```env
# Archivo .env
HUGGINGFACE_API_KEY=hf_TU_TOKEN_AQUI
```

**Obtener token:**
1. Ve a https://huggingface.co/settings/tokens
2. Crea cuenta gratis
3. Click "New token" → Tipo "Read" → Copiar

**¿Por qué?**
- Sin el token, la API no te deja usar el servicio
- Es como la "contraseña" para acceder a la IA

---

### PASO 2: Crear `.gitignore`

**Qué hace:** Evita que archivos sensibles se suban a GitHub

**Ubicación:** Raíz del proyecto (`PROYECTO1_Soccer/.gitignore`)

**Contenido clave:**
```gitignore
# Variables de entorno (NUNCA subir)
.env
*.env

# Archivos de caché Python
__pycache__/
*.py[cod]

# Configuración Streamlit
.streamlit/secrets.toml
```

**¿Por qué?**
- Si subes `.env` a GitHub → tu token es público
- Cualquiera puede robarlo y usar tu cuota
- Es una vulnerabilidad de seguridad grave

**Verificar:**
```bash
git status  # .env NO debe aparecer en la lista
```

---

### PASO 3: Actualizar `const.py`

**Qué hace:** Define configuración pública de la API

**Ubicación:** `panel/src/utils/const.py`

**Código añadido:**

```python
# ========================================
# HUGGING FACE API CONFIGURATION
# ========================================
# URL base de la API
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"

# Modelo a utilizar (Stable Diffusion 2.1)
HUGGINGFACE_MODEL = "stabilityai/stable-diffusion-2-1"

# Nombre de la variable de entorno para la API key
ENV_HUGGINGFACE_KEY = "HUGGINGFACE_API_KEY"

# Timeout para peticiones (segundos)
HUGGINGFACE_TIMEOUT = 60

# Parámetros de generación de imágenes
HUGGINGFACE_IMAGE_WIDTH = 512      # Ancho en píxeles
HUGGINGFACE_IMAGE_HEIGHT = 512     # Alto en píxeles
HUGGINGFACE_INFERENCE_STEPS = 30   # Calidad (más pasos = mejor pero más lento)
HUGGINGFACE_GUIDANCE_SCALE = 7.5   # Adherencia al prompt (7-9 es óptimo)

# Templates de prompts para diferentes tipos de generación
PROMPT_TEMPLATES = {
    'player_portrait': (
        "Professional portrait photo of {nombre}, {posicion} soccer player "
        "from {nacionalidad}, studio lighting, high quality, detailed face"
    ),
    'team_logo': (
        "Professional sports team logo for {equipo}, {colores} colors, "
        "minimalist design, vector style"
    ),
    'action_shot': (
        "Dynamic action shot of {nombre} playing soccer, "
        "professional sports photography, motion blur"
    )
}

# Mensajes de error estandarizados
ERROR_MESSAGES = {
    'no_api_key': (
        "⚠️ API Key no configurada. Por favor, añade tu token de Hugging Face "
        "en el archivo .env en la raíz del proyecto."
    ),
    'invalid_key': (
        "❌ Token inválido o sin permisos. Verifica tu API key en "
        "https://huggingface.co/settings/tokens"
    ),
    'model_loading': (
        "⏳ El modelo está cargándose. Esto puede tardar 30-60 segundos. "
        "Por favor, inténtalo de nuevo en un momento."
    ),
    'timeout': (
        "⏱️ La petición tardó demasiado. Inténtalo de nuevo."
    ),
    'generation_failed': (
        "❌ Error al generar la imagen"
    )
}

# Configuración de caché
CACHE_TTL = 3600  # Tiempo de vida del caché (1 hora)
```

**¿Por qué cada parámetro?**

- **WIDTH/HEIGHT = 512:** Equilibrio entre calidad y velocidad (API gratuita)
- **INFERENCE_STEPS = 30:** Suficientes pasos para buena calidad sin ser muy lento
- **GUIDANCE_SCALE = 7.5:** Valor óptimo para seguir el prompt sin sobreprocesar
- **TIMEOUT = 60:** Da tiempo suficiente para generación en API lenta
- **PROMPT_TEMPLATES:** Reutilizar prompts probados que dan buenos resultados

---

### PASO 4: Crear `top_players.py`

**Qué hace:** Nueva página con análisis de top jugadores + IA generativa

**Ubicación:** `panel/src/ui/top_players.py`

**Estructura:**

```python
"""
Módulo: top_players.py
Funcionalidad: Análisis de mejores jugadores + generación de retratos con IA
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import const
import os
import requests
from PIL import Image
from io import BytesIO


# ========================================
# CLASE PRINCIPAL: PlayerImageGenerator
# ========================================
class PlayerImageGenerator:
    """
    Gestiona la generación de imágenes usando Hugging Face API
    
    Responsabilidades:
    - Cargar API key desde múltiples fuentes
    - Construir prompts personalizados
    - Realizar peticiones HTTP a la API
    - Manejar errores y timeouts
    - Retornar imágenes PIL
    """
    
    def __init__(self):
        """
        Constructor: Inicializa el generador
        
        Busca la API key en orden de prioridad:
        1. st.secrets (Streamlit Cloud)
        2. Variables de entorno del sistema
        3. Archivo .env (cargado por load_dotenv)
        """
        self.api_key = self._cargar_api_key()
        self.api_url = const.HUGGINGFACE_API_URL + const.HUGGINGFACE_MODEL
    
    def _cargar_api_key(self):
        """
        Método privado para cargar la API key
        
        ¿Por qué múltiples fuentes?
        - Streamlit Cloud usa secrets.toml
        - Desarrollo local usa .env
        - Servidores usan variables de entorno del sistema
        """
        # Prioridad 1: Streamlit secrets
        if hasattr(st, 'secrets') and const.ENV_HUGGINGFACE_KEY in st.secrets:
            return st.secrets[const.ENV_HUGGINGFACE_KEY]
        
        # Prioridad 2 y 3: Variables de entorno (incluye .env ya cargado)
        return os.getenv(const.ENV_HUGGINGFACE_KEY)
    
    def generar_retrato_jugador(self, nombre_jugador, posicion, nacionalidad):
        """
        Genera un retrato profesional de un jugador
        
        Args:
            nombre_jugador (str): Ej. "Lionel Messi"
            posicion (str): Ej. "Forward", "Midfielder"
            nacionalidad (str): Ej. "Argentina"
        
        Returns:
            PIL.Image or None: Imagen generada o None si error
        """
        # Construir prompt personalizado usando template
        template = const.PROMPT_TEMPLATES['player_portrait']
        prompt = template.format(
            nombre=nombre_jugador,
            posicion=posicion,
            nacionalidad=nacionalidad
        )
        
        return self._generar_imagen(prompt)
    
    def _generar_imagen(self, prompt):
        """
        Método privado: Realiza la petición HTTP a Hugging Face
        
        Proceso:
        1. Verificar que existe API key
        2. Construir headers con Authorization
        3. Construir payload con prompt y parámetros
        4. POST request a la API
        5. Parsear respuesta según código HTTP
        6. Convertir bytes a PIL.Image
        7. Manejar errores
        """
        if not self.api_key:
            st.error(const.ERROR_MESSAGES['no_api_key'])
            return None
        
        # Headers de autenticación
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Payload con prompt y parámetros
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": const.HUGGINGFACE_IMAGE_WIDTH,
                "height": const.HUGGINGFACE_IMAGE_HEIGHT,
                "num_inference_steps": const.HUGGINGFACE_INFERENCE_STEPS,
                "guidance_scale": const.HUGGINGFACE_GUIDANCE_SCALE
            }
        }
        
        try:
            # Petición POST
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=const.HUGGINGFACE_TIMEOUT
            )
            
            # Manejar diferentes códigos de respuesta
            if response.status_code == 200:
                # Éxito: convertir bytes a imagen
                image = Image.open(BytesIO(response.content))
                return image
            
            elif response.status_code == 503:
                # Modelo cargándose (normal la primera vez)
                st.warning(const.ERROR_MESSAGES['model_loading'])
                return None
            
            elif response.status_code == 401:
                # Token inválido
                st.error(const.ERROR_MESSAGES['invalid_key'])
                return None
            
            else:
                # Error desconocido
                st.error(f"{const.ERROR_MESSAGES['generation_failed']}: {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            st.error(const.ERROR_MESSAGES['timeout'])
            return None
        
        except Exception as e:
            st.error(f"{const.ERROR_MESSAGES['generation_failed']}: {str(e)}")
            return None


# ========================================
# FUNCIÓN PRINCIPAL: render_top_players_page
# ========================================
def render_top_players_page():
    """
    Renderiza la página completa de Top Jugadores
    
    Secciones:
    1. Top 10 Jugadores Globales
    2. Top Jugadores por Posición (Tabs)
    3. Generador de Retratos con IA ⭐
    4. Duelo de Leyendas (comparación)
    """
    
    st.title("⚽ TOP Jugadores Mundiales")
    st.markdown("---")
    
    # Verificar datos en session_state
    if 'df' not in st.session_state or st.session_state.df is None:
        st.error("❌ No hay datos cargados.")
        return
    
    df = st.session_state.df
    
    # ... [SECCIÓN 1: Top 10 Global]
    # ... [SECCIÓN 2: Top por Posición]
    
    # ========================================
    # SECCIÓN 3: GENERADOR IA (LA MÁS IMPORTANTE)
    # ========================================
    st.header("🎨 Generador de Retratos con IA")
    
    # Inicializar generador
    generator = PlayerImageGenerator()
    
    # Verificar API key
    if not generator.api_key:
        st.error("""
        ❌ API Key no configurada
        
        Pasos:
        1. Ve a https://huggingface.co/settings/tokens
        2. Crea token (tipo Read)
        3. Añádelo al archivo .env
        4. Reinicia la app
        """)
    else:
        st.success("✅ API Key configurada")
        
        # Selector de jugador
        jugador_seleccionado = st.selectbox(
            "Selecciona un jugador:",
            options=df.nlargest(50, 'overall_rating')['player_name'].tolist()
        )
        
        # Botón de generación
        if st.button("🎨 Generar Retrato"):
            # Obtener datos del jugador
            jugador_data = df[df['player_name'] == jugador_seleccionado].iloc[0]
            
            # Extraer info
            nombre = jugador_data['player_name']
            posicion = jugador_data['player_positions'].split(',')[0]
            nacionalidad = jugador_data['nationality_name']
            
            # Mostrar spinner
            with st.spinner(f"Generando retrato de {nombre}..."):
                imagen = generator.generar_retrato_jugador(
                    nombre, posicion, nacionalidad
                )
            
            # Mostrar resultado
            if imagen:
                # ⭐ PERSISTENCIA: Guardar en session_state
                st.session_state.ultima_imagen_generada = imagen
                st.session_state.ultimo_jugador_generado = nombre
                
                # Mostrar imagen
                st.image(imagen, caption=f"Retrato de {nombre}")
                
                # Botón de descarga
                buffer = BytesIO()
                imagen.save(buffer, format='PNG')
                buffer.seek(0)
                
                st.download_button(
                    label="💾 Descargar",
                    data=buffer,
                    file_name=f"retrato_{nombre.replace(' ', '_')}.png",
                    mime="image/png"
                )
        
        # Mostrar última imagen generada (persistencia)
        if 'ultima_imagen_generada' in st.session_state:
            st.markdown("### Última imagen generada:")
            st.image(st.session_state.ultima_imagen_generada)
    
    # ... [SECCIÓN 4: Duelo de Leyendas]
```

**Conceptos clave:**

1. **Clase vs Funciones:**
   - Clase = Agrupa funcionalidad relacionada
   - Evita repetir código (DRY: Don't Repeat Yourself)
   - Guarda estado (self.api_key, self.api_url)

2. **Métodos privados (_prefijo):**
   - `_cargar_api_key()`, `_generar_imagen()`
   - Convención: indica que son internos, no para uso externo

3. **Session State (st.session_state):**
   - Persiste datos entre reruns de Streamlit
   - Sin esto, la imagen desaparecería al interactuar con la app

4. **BytesIO:**
   - Buffer de memoria para manejar imágenes
   - Permite descargar sin guardar archivo en disco

---

### PASO 5: Actualizar `app.py`

**Qué hacer:**

1. **Importar python-dotenv:**
```python
from dotenv import load_dotenv

# Cargar .env al inicio
load_dotenv()
```

2. **Guardar df en session_state:**
```python
# Guardar df para acceso global
st.session_state.df = df
```

3. **Integrar nueva página:**
```python
elif page == "⭐ Top Jugadores":
    from ui.top_players import render_top_players_page
    render_top_players_page()
```

**¿Por qué session_state?**
- `top_players.py` necesita acceso a los datos
- Sin session_state → tendríamos que pasar `df` como parámetro
- Con session_state → acceso global más limpio

---

### PASO 6: Crear script de prueba

**Qué hace:** Verifica que toda la configuración es correcta

**Ubicación:** `test_huggingface_setup.py` (raíz del proyecto)

**Funciones:**

```python
def verificar_archivo_env():
    """Verifica que .env existe"""
    # Busca .env en la raíz
    # Retorna True/False

def cargar_y_verificar_token():
    """Carga .env y verifica formato del token"""
    # Usa load_dotenv()
    # Verifica que no sea el ejemplo
    # Verifica que empiece con 'hf_'

def probar_conexion_api(token):
    """Hace una petición real a la API"""
    # POST request de prueba
    # Maneja códigos 200, 401, 503, 429
    # Retorna True si funciona

def verificar_dependencias():
    """Verifica que todos los paquetes están instalados"""
    # Intenta importar: streamlit, requests, PIL, dotenv
    # Lista los que faltan
```

**Uso:**
```bash
python test_huggingface_setup.py
```

**Salida esperada:**
```
============================================================
VERIFICACIÓN DE CONFIGURACIÓN - HUGGING FACE API
============================================================

============================================================
PASO 1: Verificar archivo .env
============================================================

✓ Archivo .env encontrado: C:\Users\...\PROYECTO1_Soccer\.env

============================================================
PASO 2: Verificar Token API
============================================================

✓ Módulo python-dotenv instalado correctamente
✓ Token encontrado con formato correcto: hf_abc123...

============================================================
PASO 3: Probar Conexión con API
============================================================

ℹ Enviando petición de prueba a Hugging Face...
✓ ¡Conexión exitosa con la API de Hugging Face!
✓ La generación de imágenes funcionará correctamente

============================================================
PASO 4: Verificar Dependencias
============================================================

✓ streamlit instalado
✓ requests instalado
✓ Pillow instalado
✓ python-dotenv instalado

============================================================
RESUMEN FINAL
============================================================

✓ ✅ ¡TODO CONFIGURADO CORRECTAMENTE!

ℹ Ya puedes usar la funcionalidad de generación de imágenes:
  1. Ejecuta: streamlit run panel/src/app.py
  2. Ve a la sección '⭐ Top Jugadores'
  3. Usa el generador de retratos con IA

============================================================
```

---

### PASO 7: Instalar dependencias

**Comando:**
```bash
pip install python-dotenv
```

**¿Por qué?**
- `python-dotenv` lee el archivo `.env` y carga las variables
- Sin esto, `os.getenv()` no encuentra el token

**Verificar instalación:**
```bash
pip list | grep dotenv
# Salida: python-dotenv 1.0.0
```

---

## 4. CÓDIGO DETALLADO

### 4.1 Cómo funciona `load_dotenv()`

```python
from dotenv import load_dotenv
import os

# Al llamar load_dotenv():
load_dotenv()

# Internamente hace:
# 1. Busca archivo .env en el directorio actual y padres
# 2. Lee cada línea del archivo
# 3. Parsea formato KEY=VALUE
# 4. Carga como variables de entorno del sistema

# Ejemplo de .env:
# HUGGINGFACE_API_KEY=hf_123456

# Después de load_dotenv(), puedes hacer:
api_key = os.getenv('HUGGINGFACE_API_KEY')
# api_key ahora contiene "hf_123456"
```

### 4.2 Cómo funciona `requests.post()`

```python
import requests

# Estructura de una petición HTTP POST
response = requests.post(
    url="https://api.ejemplo.com/generar",  # Destino
    headers={                                # Cabeceras
        "Authorization": "Bearer token123",  # Autenticación
        "Content-Type": "application/json"   # Tipo de datos
    },
    json={                                   # Cuerpo (payload)
        "prompt": "genera una imagen",
        "width": 512
    },
    timeout=60                               # Máximo tiempo de espera
)

# La API responde con:
# - response.status_code: Código HTTP (200, 401, 503, etc.)
# - response.content: Bytes de la respuesta
# - response.json(): Si la respuesta es JSON

# Códigos comunes:
# 200 = Éxito
# 401 = No autorizado (token inválido)
# 503 = Servicio no disponible (modelo cargándose)
# 429 = Demasiadas peticiones
```

### 4.3 Cómo funciona PIL.Image + BytesIO

```python
from PIL import Image
from io import BytesIO

# Supongamos que response.content son bytes de una imagen PNG
image_bytes = response.content  # bytes

# Convertir bytes a PIL.Image:
buffer = BytesIO(image_bytes)  # Crear buffer en memoria
image = Image.open(buffer)     # Abrir imagen desde buffer

# Ahora 'image' es un objeto PIL.Image que puedes:
image.show()                   # Ver
image.save("foto.png")         # Guardar
st.image(image)                # Mostrar en Streamlit

# Para descargar:
output_buffer = BytesIO()
image.save(output_buffer, format='PNG')
output_buffer.seek(0)  # Volver al inicio del buffer

st.download_button(
    label="Descargar",
    data=output_buffer,  # Bytes de la imagen
    file_name="imagen.png"
)
```

### 4.4 Cómo funciona st.session_state

```python
import streamlit as st

# Session State = Diccionario persistente entre reruns

# Streamlit rerun completo en CADA interacción
# Sin session_state, las variables se pierden

# ❌ PROBLEMA sin session_state:
def pagina():
    imagen = generar_imagen()  # Genera imagen
    st.image(imagen)           # Muestra imagen
    # Usuario hace click en otro botón → rerun
    # 'imagen' ya no existe → desaparece

# ✅ SOLUCIÓN con session_state:
def pagina():
    if st.button("Generar"):
        imagen = generar_imagen()
        st.session_state.mi_imagen = imagen  # Guardar
    
    # Ahora persiste entre reruns
    if 'mi_imagen' in st.session_state:
        st.image(st.session_state.mi_imagen)

# Operaciones comunes:
st.session_state.variable = valor      # Guardar
valor = st.session_state.variable      # Leer
'variable' in st.session_state         # Verificar existencia
del st.session_state.variable          # Eliminar
```

### 4.5 Estructura de un prompt efectivo

```python
# ❌ MALO - Prompt vago
prompt = "foto de Messi"

# ✅ BUENO - Prompt detallado
prompt = (
    "Professional portrait photo of Lionel Messi, "
    "Forward soccer player from Argentina, "
    "studio lighting, high quality, detailed face, "
    "photorealistic, 8k resolution"
)

# Elementos de un buen prompt:
# 1. Estilo: "Professional portrait photo"
# 2. Sujeto: "Lionel Messi, Forward soccer player"
# 3. Contexto: "from Argentina"
# 4. Calidad: "high quality, detailed face, photorealistic"
# 5. Técnica: "studio lighting, 8k resolution"

# Por eso usamos templates:
template = (
    "Professional portrait photo of {nombre}, {posicion} "
    "soccer player from {nacionalidad}, studio lighting, "
    "high quality, detailed face"
)

prompt = template.format(
    nombre="Cristiano Ronaldo",
    posicion="Forward",
    nacionalidad="Portugal"
)
# Resultado: prompt personalizado y efectivo
```

---

## 5. SEGURIDAD Y BUENAS PRÁCTICAS

### 5.1 Checklist de Seguridad

✅ **Token en .env:**
```env
# .env
HUGGINGFACE_API_KEY=hf_real_token_here
```

✅ **.env en .gitignore:**
```gitignore
# .gitignore
.env
*.env
```

✅ **Verificar antes de commit:**
```bash
git status
# .env NO debe aparecer
```

✅ **Documentar sin exponer:**
```markdown
# README.md
Para usar la IA, crea un archivo .env con tu token de Hugging Face.
No incluyas tu token real en la documentación.
```

✅ **Rotar tokens si se exponen:**
Si accidentalmente subes un token a GitHub:
1. Ve a Hugging Face → Settings → Tokens
2. Revoca el token expuesto
3. Crea uno nuevo
4. Actualiza tu .env local

### 5.2 Patrones Inseguros a Evitar

❌ **Token hardcodeado:**
```python
# ¡NUNCA HAGAS ESTO!
API_KEY = "hf_abc123xyz"  # Token expuesto en código
```

❌ **Token en comentarios:**
```python
# Mi token es hf_abc123xyz  # ¡Los comentarios también se suben!
```

❌ **Token en variables de entorno expuestas:**
```python
# Malo si subes este archivo a GitHub
API_KEY = os.getenv('HUGGINGFACE_API_KEY')  # OK
print(f"Mi token es {API_KEY}")              # ¡MALO! Lo escribes en logs
```

❌ **Token en nombres de archivo:**
```bash
# ¡No llames a tu archivo así!
backup_with_key_hf_abc123.py
```

### 5.3 Buenas Prácticas de Código

**1. Manejo de errores robusto:**
```python
try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    elif response.status_code == 503:
        st.warning("Modelo cargándose, intenta de nuevo")
    elif response.status_code == 401:
        st.error("Token inválido")
    else:
        st.error(f"Error desconocido: {response.status_code}")
        
except requests.exceptions.Timeout:
    st.error("Timeout")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

**2. Mensajes de error útiles:**
```python
# ❌ MALO
st.error("Error")

# ✅ BUENO
st.error("""
❌ API Key no configurada

Pasos para solucionar:
1. Ve a https://huggingface.co/settings/tokens
2. Crea un token (tipo Read)
3. Añádelo al archivo .env:
   HUGGINGFACE_API_KEY=tu_token_aqui
4. Reinicia la aplicación
""")
```

**3. Constantes bien nombradas:**
```python
# ❌ MALO
W = 512
H = 512
S = 30

# ✅ BUENO
HUGGINGFACE_IMAGE_WIDTH = 512
HUGGINGFACE_IMAGE_HEIGHT = 512
HUGGINGFACE_INFERENCE_STEPS = 30
```

**4. Documentación clara:**
```python
def generar_retrato_jugador(self, nombre, posicion, nacionalidad):
    """
    Genera un retrato profesional de un jugador
    
    Args:
        nombre (str): Nombre completo del jugador
        posicion (str): Posición en el campo (Forward, Midfielder, etc.)
        nacionalidad (str): País de origen
    
    Returns:
        PIL.Image or None: Imagen generada, o None si hay error
    
    Example:
        >>> generator = PlayerImageGenerator()
        >>> img = generator.generar_retrato_jugador("Messi", "Forward", "Argentina")
        >>> img.save("messi.png")
    """
    # ...código...
```

---

## 6. SOLUCIÓN DE PROBLEMAS

### Error 1: "Import dotenv could not be resolved"

**Causa:** python-dotenv no está instalado

**Solución:**
```bash
pip install python-dotenv
```

**Verificar:**
```bash
pip list | grep dotenv
```

---

### Error 2: "API Key no configurada"

**Causas posibles:**
1. Archivo .env no existe
2. .env está en la ubicación incorrecta
3. Formato incorrecto en .env
4. load_dotenv() no se ejecutó

**Solución paso a paso:**

1. **Verificar que .env existe:**
```bash
cd C:\Users\Joaquim\OneDrive\UPGRADE\PROYECTO1_Soccer
dir .env
# Debe aparecer el archivo
```

2. **Verificar contenido de .env:**
```bash
type .env
# Debe mostrar: HUGGINGFACE_API_KEY=hf_...
```

3. **Verificar formato correcto:**
```env
# ✅ CORRECTO
HUGGINGFACE_API_KEY=hf_abc123

# ❌ INCORRECTO (comillas no necesarias)
HUGGINGFACE_API_KEY="hf_abc123"

# ❌ INCORRECTO (espacios alrededor del =)
HUGGINGFACE_API_KEY = hf_abc123
```

4. **Verificar que load_dotenv() se ejecuta:**
```python
# En app.py, AL INICIO:
from dotenv import load_dotenv
load_dotenv()  # ANTES de cualquier import de tus módulos
```

5. **Debug manual:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"API Key: {os.getenv('HUGGINGFACE_API_KEY')}")
# Debe imprimir tu token
```

---

### Error 3: "Invalid API key (401)"

**Causa:** Token incorrecto, expirado o sin permisos

**Solución:**

1. **Verificar formato del token:**
   - Debe empezar con `hf_`
   - Debe tener ~30-40 caracteres

2. **Verificar que no sea el ejemplo:**
```env
# ❌ Todavía es el ejemplo
HUGGINGFACE_API_KEY=hf_TU_TOKEN_AQUI
```

3. **Crear nuevo token:**
   - Ve a https://huggingface.co/settings/tokens
   - Click "New token"
   - Nombre: "soccer-app"
   - Tipo: "Read"
   - Copiar token completo
   - Pegar en .env

4. **Reiniciar aplicación:**
```bash
# Cerrar Streamlit (Ctrl+C)
streamlit run panel/src/app.py
```

---

### Error 4: "Model is loading (503)"

**Causa:** El modelo Stable Diffusion está "dormido" en los servidores

**Solución:**
- **No es un error real**, es normal
- Espera 30-60 segundos
- Intenta de nuevo
- La aplicación lo maneja automáticamente

**Explicación:**
- Hugging Face "duerme" modelos no usados para ahorrar recursos
- La primera petición lo "despierta"
- Peticiones subsecuentes son rápidas

---

### Error 5: Generación muy lenta

**Causas:**
1. API gratuita tiene límites de velocidad
2. Muchos usuarios usando el modelo
3. Parámetros de alta calidad

**Soluciones:**

**1. Reducir calidad (más rápido):**
```python
# const.py
HUGGINGFACE_INFERENCE_STEPS = 20  # Antes era 30
HUGGINGFACE_IMAGE_WIDTH = 384     # Antes era 512
HUGGINGFACE_IMAGE_HEIGHT = 384
```

**2. Usar modelo más rápido:**
```python
# const.py
# Cambiar a modelo más pequeño
HUGGINGFACE_MODEL = "CompVis/stable-diffusion-v1-4"
```

**3. Upgrading a Hugging Face Pro:**
- $9/mes
- Sin límites de velocidad
- Generación instantánea

---

### Error 6: Imagen no persiste al interactuar

**Causa:** No se guardó en session_state

**Solución:**
```python
# ❌ MALO - Se pierde al rerun
if st.button("Generar"):
    imagen = generator.generar_retrato(...)
    st.image(imagen)  # Desaparece al siguiente clic

# ✅ BUENO - Persiste
if st.button("Generar"):
    imagen = generator.generar_retrato(...)
    st.session_state.ultima_imagen = imagen  # Guardar

if 'ultima_imagen' in st.session_state:
    st.image(st.session_state.ultima_imagen)  # Siempre visible
```

---

## 7. LECCIONES APRENDIDAS

### 7.1 Conceptos Clave

1. **Separación de Secretos y Configuración:**
   - `.env` para secretos (tokens, passwords)
   - `const.py` para configuración pública (URLs, parámetros)
   - `.gitignore` para proteger secretos

2. **Arquitectura Modular:**
   - Un archivo por funcionalidad (`top_players.py` solo para IA)
   - Evita "ensuciar" código existente
   - Facilita mantenimiento y testing

3. **Manejo de Estado en Streamlit:**
   - `st.session_state` para persistencia
   - `@st.cache_data` para optimización
   - Reruns completos en cada interacción

4. **APIs HTTP:**
   - POST request con autenticación (Bearer token)
   - Manejo de códigos de estado (200, 401, 503)
   - Timeouts para evitar esperas infinitas

5. **Manejo de Imágenes:**
   - Bytes → BytesIO → PIL.Image → Streamlit/Descarga
   - Formato PNG para calidad sin pérdidas
   - Buffer en memoria vs. archivos en disco

### 7.2 Flujo Completo Explicado

```
USUARIO                  APP                    API HUGGING FACE
  |                       |                           |
  |--- Abre app --------->|                           |
  |                       |--- load_dotenv() ---------|
  |                       |    (carga .env)           |
  |                       |                           |
  |--- Navega "Top" ----->|                           |
  |                       |--- importa top_players -->|
  |                       |                           |
  |--- Selecciona jugador-|                           |
  |                       |                           |
  |--- Click "Generar" -->|                           |
  |                       |--- Construye prompt ----->|
  |                       |                           |
  |                       |--- POST request --------->|
  |                       |    (con token)            |
  |                       |                           |
  |                       |                      <=== Procesa IA
  |                       |                           |
  |                       |<--- Bytes de imagen ------|
  |                       |                           |
  |                       |--- BytesIO → PIL.Image -->|
  |                       |                           |
  |                       |--- Guarda session_state ->|
  |                       |                           |
  |<--- Muestra imagen ---|                           |
  |                       |                           |
  |--- Click "Descargar"->|                           |
  |                       |--- Image.save(buffer) --->|
  |<--- Descarga PNG -----|                           |
```

### 7.3 Mejores Prácticas Aprendidas

1. **Siempre verificar configuración antes de usar:**
   - Crear script de prueba (`test_huggingface_setup.py`)
   - Verificar paso por paso: archivo, token, API, dependencias

2. **Mensajes de error educativos:**
   - No solo "Error", sino pasos concretos para solucionarlo
   - URLs relevantes, comandos exactos

3. **Fallbacks y recuperación:**
   - Si el modelo está cargándose (503) → mensaje útil, no error
   - Si falta API key → instrucciones claras

4. **Documentación exhaustiva:**
   - README con guía paso a paso
   - Comentarios en código explicando "por qué", no solo "qué"

5. **Testing incremental:**
   - Primero verificar .env
   - Luego verificar token
   - Luego probar API
   - Finalmente usar en la app

### 7.4 Preguntas Frecuentes Respondidas

**P: ¿Por qué no poner el token directamente en const.py?**
R: Porque const.py se sube a GitHub → el token sería público → cualquiera podría usarlo.

**P: ¿Por qué usar una clase en vez de funciones?**
R: Para agrupar funcionalidad relacionada, evitar repetir código, y guardar estado (api_key, api_url).

**P: ¿Por qué BytesIO en vez de guardar archivo?**
R: Más rápido (todo en memoria), no ensucia el disco, mejor para descargas.

**P: ¿Por qué session_state?**
R: Streamlit rerun completo en cada interacción → sin session_state las variables se pierden.

**P: ¿Por qué 512x512 y no 1024x1024?**
R: Equilibrio entre calidad y velocidad. API gratuita es lenta con imágenes grandes.

**P: ¿Puedo cambiar el modelo de IA?**
R: Sí, cambia `HUGGINGFACE_MODEL` en const.py. Opciones: sd-v1-4, sd-2-1, sd-xl (más lento pero mejor).

**P: ¿Cuánto cuesta la API?**
R: Gratis con límites. $9/mes para velocidad sin límites (Hugging Face Pro).

---

## 8. RESUMEN FINAL

### ✅ Lo que HICIMOS:

1. ✅ Creamos `.env` para almacenar token de forma segura
2. ✅ Creamos `.gitignore` para proteger secretos
3. ✅ Actualizamos `const.py` con configuración de Hugging Face
4. ✅ Creamos `top_players.py` con clase `PlayerImageGenerator`
5. ✅ Actualizamos `app.py` para integrar nueva página
6. ✅ Creamos `test_huggingface_setup.py` para verificación
7. ✅ Instalamos dependencia `python-dotenv`
8. ✅ Creamos `README_HUGGINGFACE.md` con documentación completa

### 🎯 Lo que APRENDIMOS:

- Diferencia entre secretos (.env) y configuración (const.py)
- Cómo funcionan las APIs de generación de imágenes
- Uso de python-dotenv para variables de entorno
- Requests HTTP con autenticación Bearer
- Manejo de imágenes con PIL y BytesIO
- Session state en Streamlit para persistencia
- Arquitectura modular y código limpio
- Seguridad: nunca exponer tokens en GitHub

### 🚀 PRÓXIMOS PASOS:

1. **Obtén tu token de Hugging Face:**
   - https://huggingface.co/settings/tokens

2. **Configúralo en .env:**
   ```env
   HUGGINGFACE_API_KEY=tu_token_aqui
   ```

3. **Verifica configuración:**
   ```bash
   python test_huggingface_setup.py
   ```

4. **Ejecuta la app:**
   ```bash
   streamlit run panel/src/app.py
   ```

5. **Usa el generador:**
   - Ve a "⭐ Top Jugadores"
   - Sección "🎨 Generador de Retratos con IA"
   - Selecciona jugador → Generar → ¡Disfruta!

---

**¡Implementación completa! 🎉**

Ahora tienes una app de análisis de fútbol con IA generativa, siguiendo las mejores prácticas de seguridad y arquitectura de software.
