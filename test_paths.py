"""
Script de prueba para verificar que las rutas funcionan correctamente
antes de subir a producción en Streamlit Cloud.

Ejecutar desde la raíz del proyecto:
    python test_paths.py
"""

import os
import sys

# Añadir el directorio panel/src al path para poder importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'panel', 'src'))

def test_paths():
    """Prueba que todas las rutas estén correctamente configuradas."""
    print("=" * 60)
    print("VERIFICACIÓN DE RUTAS PARA DEPLOYMENT")
    print("=" * 60)
    
    # 1. Verificar estructura del proyecto
    print("\n1. Verificando estructura del proyecto...")
    raiz = os.path.dirname(os.path.abspath(__file__))
    print(f"   Raíz del proyecto: {raiz}")
    
    # 2. Verificar archivo CSV
    print("\n2. Verificando archivo de datos...")
    csv_path = os.path.join(raiz, 'data', 'data.csv')
    if os.path.exists(csv_path):
        size_mb = os.path.getsize(csv_path) / (1024 * 1024)
        print(f"   ✅ data.csv encontrado")
        print(f"   📊 Tamaño: {size_mb:.2f} MB")
    else:
        print(f"   ❌ ERROR: data.csv NO encontrado en {csv_path}")
        return False
    
    # 3. Verificar módulo data_loader
    print("\n3. Verificando módulo data_loader...")
    try:
        from utils import data_loader
        print(f"   ✅ Módulo data_loader importado correctamente")
        print(f"   📁 Ruta configurada: {data_loader.RUTA_ABSOLUTA_CSV}")
        
        # Verificar que la ruta configurada coincide
        if os.path.exists(data_loader.RUTA_ABSOLUTA_CSV):
            print(f"   ✅ Archivo accesible desde data_loader")
        else:
            print(f"   ❌ ERROR: Archivo NO accesible desde data_loader")
            print(f"   Expected: {csv_path}")
            print(f"   Got: {data_loader.RUTA_ABSOLUTA_CSV}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR al importar data_loader: {e}")
        return False
    
    # 4. Verificar requirements.txt
    print("\n4. Verificando requirements.txt...")
    req_path = os.path.join(raiz, 'requirements.txt')
    if os.path.exists(req_path):
        print(f"   ✅ requirements.txt encontrado")
    else:
        print(f"   ❌ ERROR: requirements.txt NO encontrado")
        return False
    
    # 5. Verificar app.py
    print("\n5. Verificando app.py...")
    app_path = os.path.join(raiz, 'panel', 'src', 'app.py')
    if os.path.exists(app_path):
        print(f"   ✅ app.py encontrado en panel/src/app.py")
    else:
        print(f"   ❌ ERROR: app.py NO encontrado")
        return False
    
    # 6. Verificar configuración Streamlit
    print("\n6. Verificando configuración Streamlit...")
    config_path = os.path.join(raiz, '.streamlit', 'config.toml')
    if os.path.exists(config_path):
        print(f"   ✅ .streamlit/config.toml encontrado")
    else:
        print(f"   ⚠️  ADVERTENCIA: .streamlit/config.toml NO encontrado (opcional)")
    
    # 7. Verificar .gitignore
    print("\n7. Verificando .gitignore...")
    gitignore_path = os.path.join(raiz, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'data.csv' in content:
                print(f"   ⚠️  ADVERTENCIA: data.csv está en .gitignore (no se subirá a Git)")
            else:
                print(f"   ✅ data.csv NO está en .gitignore (se subirá correctamente)")
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS VERIFICACIONES PASARON CORRECTAMENTE")
    print("=" * 60)
    print("\nListo para deployment en Streamlit Cloud!")
    print("Punto de entrada: panel/src/app.py")
    return True

if __name__ == "__main__":
    success = test_paths()
    sys.exit(0 if success else 1)
