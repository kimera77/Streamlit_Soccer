# 🚀 Deployment en Streamlit Cloud

## Configuración del Deployment

### 1. Archivo principal
- **Main file path**: `panel/src/app.py`

### 2. Python version
- **Python**: 3.11 o superior

### 3. Secrets (Variables de entorno)
Si usas la API de Hugging Face para generar imágenes, añade en Streamlit Cloud:

```toml
HUGGINGFACE_API_KEY = "tu_api_key_aqui"
```

**Configuración en Streamlit Cloud:**
1. Ve a tu app en Streamlit Cloud
2. Click en "Settings" (⚙️)
3. Ve a "Secrets"
4. Pega tu clave de API

### 4. Estructura de archivos necesaria

```
Streamlit_Soccer/
├── data/
│   └── data.csv          ← IMPORTANTE: Este archivo debe estar en el repo
├── panel/
│   └── src/
│       ├── app.py        ← Punto de entrada
│       ├── ui/
│       └── utils/
├── .streamlit/
│   └── config.toml       ← Configuración de tema
├── requirements.txt      ← Dependencias
└── README.md
```

### 5. Checklist antes de deployment

- [ ] El archivo `data/data.csv` está en el repositorio
- [ ] El archivo `requirements.txt` está actualizado
- [ ] No hay rutas absolutas (tipo `C:/Users/...`)
- [ ] Las variables de entorno están en Streamlit Secrets
- [ ] El archivo `.env` NO está en el repositorio (está en .gitignore)

### 6. Comandos Git para deployment

```bash
# Verificar cambios
git status

# Añadir todos los cambios
git add .

# Commit
git commit -m "Preparado para deployment en Streamlit Cloud"

# Push a main
git push origin main
```

### 7. URL del deployment
Una vez deployado, tu app estará disponible en:
```
https://[tu-usuario]-streamlit-soccer-[hash].streamlit.app
```

## Notas importantes

- ✅ **CSV incluido**: El archivo `data.csv` ahora está en el repositorio (anteriormente usábamos SQLite que pesaba demasiado)
- ✅ **Rutas relativas**: Todas las rutas usan `__file__` y `os.path` para ser portables
- ✅ **Sin SQLite**: SQLite ya no se usa (código comentado) para reducir peso
- ⚠️ **API Key**: Si usas la generación de imágenes IA, necesitas configurar `HUGGINGFACE_API_KEY` en Secrets
