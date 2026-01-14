"""
Archivo de constantes del proyecto Soccer Analytics
Centraliza todas las configuraciones y valores fijos usados en la aplicación.
"""

# ========== CONFIGURACIÓN DE ARCHIVOS DE DATOS ==========
SQL_FILE_NAME = "data.sqlite"
CSV_FILE_NAME = "data.csv"

# ========== CONFIGURACIÓN DE API DE HUGGING FACE ==========
# URL base de la API de Inference
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"

# Modelo de generación de imágenes a utilizar
# FLUX.1-schnell: Modelo avanzado 2024, alta calidad, SIN licencia requerida ⭐⭐⭐⭐⭐
HUGGINGFACE_MODEL = "black-forest-labs/FLUX.1-schnell"

# Modelos alternativos (en orden de preferencia si el principal falla)
HUGGINGFACE_FALLBACK_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",  # SDXL Base - Excelente calidad, sin licencia
    "black-forest-labs/FLUX.1-dev",              # FLUX dev - Más potente pero más lento
]

# MODELOS REALISTAS (comentados - requieren aceptar licencia en Hugging Face)
# Para usar estos modelos, ve a la URL del modelo y acepta la licencia primero:
# - Realistic Vision v5.1: "SG161222/Realistic_Vision_V5.1_noVAE"
#   URL: https://huggingface.co/SG161222/Realistic_Vision_V5.1_noVAE
# - epiCRealism: "emilianJR/epiCRealism"
#   URL: https://huggingface.co/emilianJR/epiCRealism
# - AbsoluteReality: "digiplay/AbsoluteReality_v1.8.1"
#   URL: https://huggingface.co/digiplay/AbsoluteReality_v1.8.1

# Parámetros de generación de imágenes
# Optimizado para FLUX.1-schnell (rápido y de alta calidad)
HUGGINGFACE_IMAGE_WIDTH = 768   # Resolución alta pero rápida
HUGGINGFACE_IMAGE_HEIGHT = 768
HUGGINGFACE_INFERENCE_STEPS = 4  # FLUX es muy eficiente con 4 pasos
HUGGINGFACE_GUIDANCE_SCALE = 3.5  # Guidance moderado para realismo

# Nombre de la variable de entorno para el API key
ENV_HUGGINGFACE_KEY = "HUGGINGFACE_API_KEY"

# Timeout para requests a la API (segundos)
HUGGINGFACE_TIMEOUT = 60

# ========== PROMPTS PARA GENERACIÓN DE IMÁGENES ==========
# Prompts optimizados para FLUX.1-schnell (genera imágenes realistas)
PROMPT_TEMPLATES = {
    'player_portrait': """
    Professional sports photography portrait of {player_name},
    {posicion} football player from {nacionalidad},
    realistic photograph, high quality, detailed facial features,
    athletic build, confident expression,
    wearing football jersey, stadium background blurred,
    natural lighting, photorealistic, 8k resolution,
    sports magazine cover style
    """,
    
    'team_logo': """
    Professional football club logo design for {equipo},
    {colores} color scheme,
    modern minimalist emblem, shield or circular shape,
    clean vector style, iconic symbol,
    no text, white background,
    high quality, sharp details
    """,
    
    'action_shot': """
    Dynamic sports photography of {player_name} playing football,
    professional action shot, motion captured mid-game,
    football stadium atmosphere, crowd blurred in background,
    dramatic lighting, photorealistic, high speed photography,
    sports illustrated style, 8k quality
    """
}

# ========== MENSAJES DE ERROR ==========
ERROR_MESSAGES = {
    'no_api_key': f"⚠️ Variable de entorno '{ENV_HUGGINGFACE_KEY}' no configurada. No se podrán generar imágenes con IA.",
    'api_error': "❌ Error al conectar con la API de Hugging Face",
    'model_loading': "⏳ El modelo se está cargando. Intenta de nuevo en 20-30 segundos.",
    'invalid_token': "❌ Token inválido o sin permisos de Inference",
    'timeout': "⏱️ Timeout: La generación tomó demasiado tiempo",
    'generation_failed': "❌ Error al generar imagen"
}