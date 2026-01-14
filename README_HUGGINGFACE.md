# 🎨 Configuración de IA Generativa - Hugging Face

## 📋 Descripción

Esta funcionalidad permite generar retratos artísticos de jugadores de fútbol usando **Inteligencia Artificial** (Stable Diffusion 2.1) a través de la API gratuita de Hugging Face.

---

## 🚀 Guía de Configuración Rápida

### **Paso 1: Instalar Dependencias**

Asegúrate de tener instalados los siguientes paquetes Python:

```bash
pip install python-dotenv requests pillow streamlit
```

### **Paso 2: Obtener Token de Hugging Face**

1. Ve a [https://huggingface.co/](https://huggingface.co/)
2. Crea una cuenta gratuita (si no tienes una)
3. Ve a **Settings** → **Access Tokens**: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Haz clic en **"New token"**
5. Dale un nombre (ej: "soccer-ai-generator")
6. Selecciona tipo **"Read"** (es suficiente)
7. Copia el token generado (empieza con `hf_...`)

### **Paso 3: Configurar el Token en tu Proyecto**

1. Abre el archivo **`.env`** en la raíz del proyecto
2. Reemplaza `hf_TU_TOKEN_AQUI` con tu token real:

```env
HUGGINGFACE_API_KEY=hf_tu_token_copiado_aqui
```

3. Guarda el archivo

⚠️ **IMPORTANTE:** Nunca subas el archivo `.env` a GitHub (ya está en `.gitignore`)

### **Paso 4: Verificar Configuración**

Ejecuta el script de prueba para verificar que todo funcione:

```bash
python test_huggingface_setup.py
```

Si todo está correcto, verás:
```
✓ Archivo .env encontrado
✓ Token encontrado con formato correcto
✓ ¡Conexión exitosa con la API de Hugging Face!
✓ streamlit instalado
✓ requests instalado
✓ Pillow instalado
✓ python-dotenv instalado

✅ ¡TODO CONFIGURADO CORRECTAMENTE!
```

### **Paso 5: Usar la Aplicación**

```bash
streamlit run panel/src/app.py
```

Luego ve a la sección **"⭐ Top Jugadores"** y usa el generador de retratos.

---

## 📁 Archivos Creados/Modificados

### **Archivos Nuevos:**
- `.env` - Variables de entorno (API keys)
- `.gitignore` - Protege archivos sensibles
- `panel/src/ui/top_players.py` - Página de Top Jugadores con IA
- `test_huggingface_setup.py` - Script de verificación

### **Archivos Modificados:**
- `panel/src/utils/const.py` - Configuración de Hugging Face
- `panel/src/app.py` - Integración de nueva página

---

## 🎨 Funcionalidades Disponibles

### **1. Top 10 Jugadores Globales**
- Ranking de los mejores jugadores del mundo
- Gráfico de barras con ratings
- Tabla con datos completos

### **2. Top Jugadores por Posición**
- Porteros, Defensas, Centrocampistas, Delanteros
- Top 5 de cada posición
- Estadísticas promedio

### **3. Generador de Retratos con IA** ⭐ (NOVEDAD)
- Selecciona cualquier jugador del Top 50
- Genera un retrato artístico único
- Descarga la imagen generada
- Usa Stable Diffusion 2.1

### **4. Duelo de Leyendas**
- Compara dos jugadores top
- Radar chart comparativo
- Tabla de estadísticas detalladas

---

## ⚙️ Configuración Técnica

### **Constantes en `const.py`:**

```python
# API Configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
HUGGINGFACE_MODEL = "stabilityai/stable-diffusion-2-1"
ENV_HUGGINGFACE_KEY = "HUGGINGFACE_API_KEY"

# Image Generation Parameters
HUGGINGFACE_IMAGE_WIDTH = 512
HUGGINGFACE_IMAGE_HEIGHT = 512
HUGGINGFACE_INFERENCE_STEPS = 30
HUGGINGFACE_GUIDANCE_SCALE = 7.5
HUGGINGFACE_TIMEOUT = 60

# Prompt Templates
PROMPT_TEMPLATES = {
    'player_portrait': "Professional portrait photo of {nombre}, {posicion} soccer player from {nacionalidad}, studio lighting, high quality, detailed face",
    'team_logo': "Professional sports team logo for {equipo}, {colores} colors, minimalist design, vector style",
    'action_shot': "Dynamic action shot of {nombre} playing soccer, professional sports photography, motion blur"
}
```

### **Clase `PlayerImageGenerator`:**

```python
class PlayerImageGenerator:
    def __init__(self)
    def generar_retrato_jugador(nombre, posicion, nacionalidad)
    def generar_logo_equipo(nombre_equipo, colores)
    def _generar_imagen(prompt)  # Método privado
```

---

## 🔒 Seguridad

### **¿Por qué usar `.env`?**
- Separa **secretos** (API keys) de **código**
- Evita exponer tokens en GitHub
- Permite diferentes configuraciones por entorno

### **¿Qué va en cada archivo?**

**`.env`** (SECRETOS - NO subir a GitHub):
```env
HUGGINGFACE_API_KEY=hf_token_secreto
DATABASE_PASSWORD=mi_password
```

**`const.py`** (CONFIGURACIÓN PÚBLICA - OK para GitHub):
```python
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
HUGGINGFACE_MODEL = "stabilityai/stable-diffusion-2-1"
```

### **Archivos Protegidos en `.gitignore`:**
```gitignore
.env
*.env
.env.local
.streamlit/secrets.toml
__pycache__/
```

---

## 🐛 Solución de Problemas

### **Error: "API Key no configurada"**
- Verifica que el archivo `.env` existe
- Asegúrate de que `HUGGINGFACE_API_KEY` está correctamente escrito
- Reinicia la aplicación Streamlit

### **Error: "Invalid API key"**
- Verifica que copiaste el token completo
- Asegúrate de que empieza con `hf_`
- Crea un nuevo token en Hugging Face

### **Error: "Model is loading (503)"**
- Es normal la primera vez
- Espera 30-60 segundos
- Vuelve a intentar

### **Error: "Import dotenv could not be resolved"**
- Instala python-dotenv:
  ```bash
  pip install python-dotenv
  ```

### **Generación muy lenta**
- Es normal: la API gratuita tiene límites
- Puede tardar 10-30 segundos por imagen
- La primera generación siempre tarda más

---

## 📊 Límites de la API Gratuita

Hugging Face ofrece:
- ✅ **Gratis** para uso personal
- ✅ **Sin límite** de generaciones diarias
- ⚠️ **Lento** en horas pico
- ⚠️ Puede tardar si el modelo se "duerme"

**Alternativas si necesitas más velocidad:**
- Hugging Face Pro ($9/mes) - sin límites de velocidad
- Local con Stable Diffusion (requiere GPU potente)
- Otras APIs: Leonardo.AI, Stability AI, etc.

---

## 📚 Recursos Adicionales

- [Documentación Hugging Face API](https://huggingface.co/docs/api-inference/index)
- [Stable Diffusion 2.1 Model](https://huggingface.co/stabilityai/stable-diffusion-2-1)
- [Python-dotenv Docs](https://pypi.org/project/python-dotenv/)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)

---

## 👨‍💻 Arquitectura del Código

```
proyecto_soccer/
│
├── .env                          # Secretos (NO subir a GitHub)
├── .gitignore                    # Protege archivos sensibles
├── test_huggingface_setup.py     # Script de verificación
│
└── panel/src/
    ├── app.py                    # App principal (integra top_players)
    │
    ├── utils/
    │   └── const.py              # Configuración pública de Hugging Face
    │
    └── ui/
        ├── home.py               # Página inicio (sin IA)
        ├── players.py            # Análisis jugadores (sin IA)
        ├── teams.py              # Análisis equipos (sin IA)
        ├── leagues.py            # Análisis ligas (sin IA)
        └── top_players.py        # ⭐ NUEVA - Con IA generativa
```

**Principio de diseño:** La IA está **aislada** en `top_players.py` → no "ensucia" otros archivos.

---

## ✅ Checklist de Configuración

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install python-dotenv requests pillow streamlit`)
- [ ] Cuenta de Hugging Face creada
- [ ] Token generado en Hugging Face
- [ ] Archivo `.env` creado con el token
- [ ] Script de prueba ejecutado exitosamente
- [ ] Aplicación Streamlit funcionando
- [ ] Generación de imágenes probada

---

**¡Listo para usar! 🎉**

Si tienes problemas, ejecuta primero `test_huggingface_setup.py` para diagnosticar.
