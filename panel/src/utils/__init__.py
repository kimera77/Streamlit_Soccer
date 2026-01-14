"""
Paquete de utilidades para la aplicación Soccer Analytics.

Módulos disponibles:
- data_loader: Carga y procesamiento de datos
- const: Constantes y configuraciones
- config: Configuración de la aplicación
"""

# Hacer disponibles las funciones principales
from .data_loader import load_data, get_data_info, get_load_info, delete_csv

__all__ = ['load_data', 'get_data_info', 'get_load_info', 'delete_csv']
