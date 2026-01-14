# ⚽ Soccer Analytics - Proyecto de Análisis de Fútbol

Aplicación de análisis de datos de fútbol con visualizaciones interactivas y generación de imágenes con IA.

## 📋 Descripción

Este proyecto incluye:
- **Dashboard interactivo** con Streamlit para análisis de jugadores, equipos y ligas
- **Visualizaciones** con Plotly para gráficos dinámicos
- **Generación de imágenes con IA** usando Hugging Face API
- **Notebooks Jupyter** para análisis de datos y machine learning

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd PROYECTO1_Soccer
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Crear un archivo `.env` en la raíz del proyecto:
```
HUGGINGFACE_API_KEY=tu_token_aqui
```

Para obtener tu API key de Hugging Face:
1. Visita https://huggingface.co/settings/tokens
2. Crea un nuevo token de acceso
3. Cópialo en el archivo `.env`

## 💻 Uso

### Ejecutar la aplicación
```bash
cd panel/src
streamlit run app.py
```
La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 🛠️ Tecnologías

- **Python 3.12**
- **Streamlit** - Framework web interactivo
- **Pandas** - Manipulación de datos
- **Plotly** - Visualizaciones interactivas
- **SQLAlchemy** - Base de datos
- **Hugging Face** - Generación de imágenes con IA
- **Jupyter** - Notebooks para análisis

## 📝 Funcionalidades

- 📊 Análisis detallado de jugadores y equipos
- 🏆 Estadísticas de ligas
- 📈 Gráficos interactivos y visualizaciones
- 🤖 Generación de imágenes de jugadores con IA
- 📓 Notebooks de análisis de datos

## 📁 Estructura del Proyecto

```
PROYECTO1_Soccer/
├── data/                    # Datos del proyecto
│   └── data.csv
├── panel/                   # Aplicación Streamlit
│   └── src/
│       ├── app.py          # Aplicación principal
│       ├── ui/             # Páginas de la interfaz
│       │   ├── dashboard.py
│       │   ├── home.py
│       │   ├── iaPlayers.py
│       │   ├── leagues.py
│       │   ├── players.py
│       │   └── teams.py
│       └── utils/          # Utilidades
│           ├── config.py
│           ├── const.py
│           └── data_loader.py
├── NOTEBOOK_aprendizaje.ipynb
├── NOTEBOOK_tratamientoDatos.ipynb
├── README.md
└── requirements.txt
```