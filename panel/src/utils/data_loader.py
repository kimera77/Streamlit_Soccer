"""
Módulo de carga y preparación de datos para la app.

Objetivo: dejar un flujo claro, con funciones pequeñas y comentarios explícitos
sobre las transformaciones (casts, coerciones, rellenos de NaN, etc.).

API pública conservada:
  - main() -> pd.DataFrame
  - load_data() -> Tuple[pd.DataFrame, dict]
  - get_data_info(), get_load_info(), delete_csv()
"""

import os
import time
import sqlite3
from sqlalchemy import create_engine
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from .const import SQL_FILE_NAME, CSV_FILE_NAME


# ============================
# 🔧 Configuración y constantes
# ============================

# Directorio de datos (centralizamos rutas para legibilidad)
DATA_DIR = 'C:/Users/Joaquim/OneDrive/UPGRADE/PROYECTO1_Soccer/data'
RUTA_ABSOLUTA_DB = os.path.join(DATA_DIR, 'data.sqlite')
RUTA_ABSOLUTA_CSV = os.path.join(DATA_DIR, 'data.csv')

# Variable global para almacenar información de carga
_load_info = {
    'csv_already_existed': None,  # None = no inicializado todavía
    'processing_time': 0.0,
    'timestamp': None,
}

# Nombres de tablas en SQLite
TABLA_JUGADOR = 'Player'
TABLA_ATRIBUTOS = 'Player_Attributes'
TABLA_PARTIDO = 'Match'
TABLA_EQUIPO = 'Team'
TABLA_LIGA = 'League'
TABLA_PAIS = 'Country'

# Columnas seleccionadas para cada tabla (optimizamos lecturas)
COLUMNAS_JUGADOR = "player_api_id, player_name, birthday, height, weight"
COLUMNAS_ATRIBUTOS = (
    "player_api_id, date, overall_rating, preferred_foot, "
    "attacking_work_rate, defensive_work_rate, ball_control, dribbling, finishing, "
    "free_kick_accuracy, heading_accuracy, short_passing, shot_power, penalties, "
    "acceleration, sprint_speed, agility, stamina, jumping, aggression, gk_diving, gk_reflexes"
)
COLUMNAS_PARTIDO = (
    "date, match_api_id, home_team_api_id, away_team_api_id, league_id, "
    "home_player_1, home_player_2, home_player_3, home_player_4, home_player_5, "
    "home_player_6, home_player_7, home_player_8, home_player_9, home_player_10, home_player_11, "
    "away_player_1, away_player_2, away_player_3, away_player_4, away_player_5, "
    "away_player_6, away_player_7, away_player_8, away_player_9, away_player_10, away_player_11"
)
COLUMNAS_EQUIPO = "team_api_id, team_long_name"
COLUMNAS_LIGA = "id, country_id, name"
COLUMNAS_PAIS = "id, name"

# Claves de unión (para no repetir literales)
COLUMNA_CLAVE = 'player_api_id'
ID_EQUIPO_CLAVE = 'team_api_id'
ID_LIGA_CLAVE = 'league_id'
ID_PAIS_CLAVE = 'country_id'


def _conectar_sqlite(db_path: str) -> sqlite3.Connection:
    """Abre conexión a SQLite y devuelve el objeto conexión."""
    return sqlite3.connect(db_path)


def _cargar_tablas(conn: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """Lee las tablas necesarias de SQLite usando solo columnas relevantes.

    Notas de manipulación:
    - League.name -> renombrado a 'league_name'
    - Country.name -> renombrado a 'country_name'
    """
    leer = pd.read_sql_query
    dfs = {
        # Lecturas directas desde SQLite con selección de columnas mínima
        'player': leer(f'SELECT {COLUMNAS_JUGADOR} FROM "{TABLA_JUGADOR}"', conn),
        'attributes': leer(f'SELECT {COLUMNAS_ATRIBUTOS} FROM "{TABLA_ATRIBUTOS}"', conn),
        'match': leer(f'SELECT {COLUMNAS_PARTIDO} FROM "{TABLA_PARTIDO}"', conn),
        'team': leer(f'SELECT {COLUMNAS_EQUIPO} FROM "{TABLA_EQUIPO}"', conn),
        # CAST/RENAME: 'name' -> 'league_name' para evitar colisiones y dar semántica
        'league': leer(f'SELECT {COLUMNAS_LIGA} FROM "{TABLA_LIGA}"', conn).rename(columns={'name': 'league_name'}),
        # CAST/RENAME: 'name' -> 'country_name' por el mismo motivo
        'country': leer(f'SELECT {COLUMNAS_PAIS} FROM "{TABLA_PAIS}"', conn).rename(columns={'name': 'country_name'}),
    }
    return dfs


def _preparar_atributos_temporada(df_attributes: pd.DataFrame) -> Tuple[pd.DataFrame, list, list]:
    """Filtra y agrega atributos para la temporada 2015-2016.

    Transformaciones clave:
    - df_attributes['date'] -> pd.to_datetime (cast explícito a fecha)
    - Para numéricas: median por jugador (reduce ruido temporal)
    - Para texto: moda (mayor frecuencia); si hay varias, se toma la primera
    """
    df = df_attributes.copy()
    # CAST: texto -> fecha (Datetime[ns]) para permitir filtros/agrupaciones temporales
    df['date'] = pd.to_datetime(df['date'])

    # Filtrado de rango de fechas para temporada 2015-2016
    df_temp = df[(df['date'] >= '2015-08-01') & (df['date'] <= '2016-07-31')].copy()

    # Identificar columnas numéricas para mediana y de texto para moda
    cols_num = df_temp.select_dtypes(include=['number']).columns.tolist()
    cols_num = [c for c in cols_num if c != COLUMNA_CLAVE]
    cols_text = [c for c in df_temp.columns if c not in cols_num and c not in [COLUMNA_CLAVE, 'date']]

    # AGREGA: columnas numéricas por MEDIANA (robusta a outliers)
    agg: Dict[str, str] = {c: 'median' for c in cols_num}
    for c in cols_text:
        # AGREGA: columnas de texto por MODA (valor más frecuente)
        agg[c] = pd.Series.mode

    df_final = df_temp.groupby(COLUMNA_CLAVE, as_index=False).agg(agg)

    # pd.Series.mode puede devolver una lista/serie; nos quedamos con el primer valor
    for c in cols_text:
        if c in df_final.columns:
            # NORMALIZA: mode puede devolver lista/serie -> tomamos el primer valor
            df_final[c] = df_final[c].apply(lambda x: x[0] if isinstance(x, (list, pd.Series, np.ndarray)) and len(x) > 0 else x)

    # Para jugadores sin registros en temporada, usamos el último disponible <= 2016-07-31
    jugadores_con_datos = set(df_final[COLUMNA_CLAVE])
    df_hasta_2016 = df[df['date'] <= '2016-07-31'].copy()
    df_faltantes = df_hasta_2016[~df_hasta_2016[COLUMNA_CLAVE].isin(jugadores_con_datos)]
    cols_atributos = cols_num + cols_text
    if len(df_faltantes) > 0:
        df_falt_ult = (
            df_faltantes.sort_values(by=[COLUMNA_CLAVE, 'date'], ascending=[True, False])
            .drop_duplicates(subset=[COLUMNA_CLAVE], keep='first')
        )
        df_final = pd.concat([df_final, df_falt_ult[[COLUMNA_CLAVE] + cols_atributos]], ignore_index=True)

    return df_final, cols_num, cols_text


def _asignar_equipo_liga_pais(
    df_attributes_final: pd.DataFrame,
    df_match: pd.DataFrame,
    df_team: pd.DataFrame,
    df_league: pd.DataFrame,
    df_country: pd.DataFrame,
) -> pd.DataFrame:
    """Asigna equipo, liga y país más recientes de 2016 a cada jugador.

    Transformaciones clave:
    - df_match['date'] -> pd.to_datetime (cast explícito)
    - Melt para obtener una fila por jugador-partido
    - Determinar home/away mirando el nombre de la columna original (variable)
    - Merge sucesivos para incorporar nombres de equipo, liga y país
    - Drop de jugadores sin equipo asignado (NaN)
    """
    # Cast de texto a fecha
    match = df_match.copy()
    # CAST: texto -> fecha (Datetime[ns]) para extraer año y ordenar
    match['date'] = pd.to_datetime(match['date'])
    match_2016 = match[match['date'].dt.year == 2016].copy()

    cols_jugadores = [c for c in match_2016.columns if 'player' in c]
    df_jug_partido = (
        pd.melt(
            match_2016,
            id_vars=['match_api_id', 'date', 'home_team_api_id', 'away_team_api_id', 'league_id'],
            value_vars=cols_jugadores,
            value_name=COLUMNA_CLAVE,
        )
        # DROPNA: quitamos entradas sin player_id
        .dropna(subset=[COLUMNA_CLAVE])
        # CAST: player_api_id -> int para garantizar claves consistentes en los merges
        .astype({COLUMNA_CLAVE: int})
    )

    df_ult = (
        df_jug_partido.sort_values(by=[COLUMNA_CLAVE, 'date'], ascending=[True, False])
        .drop_duplicates(subset=[COLUMNA_CLAVE], keep='first')
        .copy()
    )

    def _equipo_por_variable(row) -> int:
        return row['home_team_api_id'] if 'home_player' in row['variable'] else row['away_team_api_id']

    df_ult[ID_EQUIPO_CLAVE] = df_ult.apply(_equipo_por_variable, axis=1)

    puente = df_ult[[COLUMNA_CLAVE, ID_EQUIPO_CLAVE, ID_LIGA_CLAVE]]

    # MERGE: añadimos claves de equipo y liga obtenidas en el último partido de 2016
    out = df_attributes_final.merge(puente, on=COLUMNA_CLAVE, how='left')
    # MERGE: nombre del equipo por ID
    out = out.merge(df_team[[ID_EQUIPO_CLAVE, 'team_long_name']], on=ID_EQUIPO_CLAVE, how='left')
    out = out.merge(
        df_league[['id', 'league_name', ID_PAIS_CLAVE]].rename(columns={'id': ID_LIGA_CLAVE}),
        on=ID_LIGA_CLAVE,
        how='left',
    )
    out = out.merge(
        df_country[['id', 'country_name']].rename(columns={'id': ID_PAIS_CLAVE}),
        on=ID_PAIS_CLAVE,
        how='left',
    )

    # DROPNA: eliminamos jugadores sin equipo asignado tras los merges
    out.dropna(subset=['team_long_name'], inplace=True)
    return out


def _limpiar_tipos_y_nans(df_attributes_final: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos y rellena faltantes.

    Transformaciones clave por columna numérica:
      - pd.to_numeric(..., errors='coerce')  -> fuerza numérico; valores inválidos -> NaN
      - fillna(median)                       -> imputación robusta
      - astype(int)                          -> cast final a entero

    Para columnas de texto (foot/work_rate):
      - fillna(moda o 'unknown')
    """
    df = df_attributes_final.copy()

    columnas_excluir = [
        COLUMNA_CLAVE,
        'date',
        ID_EQUIPO_CLAVE,
        ID_LIGA_CLAVE,
        ID_PAIS_CLAVE,
        'team_long_name',
        'league_name',
        'country_name',
    ]
    columnas_estadisticas = [c for c in df.columns if c not in columnas_excluir]
    columnas_texto = ['preferred_foot', 'attacking_work_rate', 'defensive_work_rate']
    columnas_numericas = [c for c in columnas_estadisticas if c not in columnas_texto]

    for c in columnas_numericas:
        # COERCE: convertimos a numérico; strings inválidos -> NaN
        df[c] = pd.to_numeric(df[c], errors='coerce')
        # FILLNA: imputación con la mediana de la columna
        mediana = df[c].median()
        df[c] = df[c].fillna(mediana)
        # CAST: integramos el tipo final como entero
        df[c] = df[c].astype(int)

    for c in columnas_texto:
        if c in df.columns:
            # FILLNA (texto): usamos la moda, o 'unknown' si no hay
            moda = df[c].mode()
            default = moda[0] if len(moda) > 0 else 'unknown'
            df[c] = df[c].fillna(default)

    return df


def _unir_player_con_atributos(df_player: pd.DataFrame, df_attributes_final: pd.DataFrame) -> pd.DataFrame:
    """Merge final por player_api_id y cleanup de IDs auxiliares."""
    # MERGE FINAL: unimos por player_api_id; inner asegura registros consistentes
    df = pd.merge(df_player, df_attributes_final, on=COLUMNA_CLAVE, how='inner')
    # CLEANUP: eliminamos IDs auxiliares que ya no aportan valor
    df.drop(columns=[ID_EQUIPO_CLAVE, ID_LIGA_CLAVE, ID_PAIS_CLAVE], inplace=True, errors='ignore')
    return df


def _registrar_sql_en_memoria(df_final: pd.DataFrame) -> None:
    """Crea motor SQLite en memoria y registra el DataFrame para análisis ad-hoc."""
    engine = create_engine('sqlite:///:memory:')
    df_final.to_sql('jugadores_2016', engine, index=False, if_exists='replace')


def main() -> pd.DataFrame:
    """Controla el flujo de carga, limpieza, unión y persistencia de datos."""
    global _load_info
    start_time = time.time()

    # 0) Si ya existe el CSV consolidado, lo usamos directamente
    if os.path.exists(RUTA_ABSOLUTA_CSV):
        print(f"✅ ¡Éxito! El archivo consolidado '{CSV_FILE_NAME}' ya existe.")
        df_final = pd.read_csv(RUTA_ABSOLUTA_CSV)
        _load_info['csv_already_existed'] = True
    else:
        print(f"❌ Archivo '{CSV_FILE_NAME}' no encontrado. Iniciando flujo de Carga, Limpieza y Unión...")
        _load_info['csv_already_existed'] = False

        if not os.path.exists(RUTA_ABSOLUTA_DB):
            print(f"🚨 ERROR: No se encontró la base de datos en la ruta: {RUTA_ABSOLUTA_DB}")
            return pd.DataFrame()

        # 1) Conectar y cargar tablas
        try:
            conn = _conectar_sqlite(RUTA_ABSOLUTA_DB)
            print(f"Conexión a SQLite ({SQL_FILE_NAME}) establecida con éxito.")
            tablas = _cargar_tablas(conn)
        except sqlite3.Error as e:
            print(f"❌ Error durante la carga de SQLite: {e}")
            return pd.DataFrame()
        finally:
            try:
                conn.close()
                print("Conexión a SQLite cerrada.")
            except Exception:
                pass

        df_player = tablas['player']
        df_attributes = tablas['attributes']
        df_match = tablas['match']
        df_team = tablas['team']
        df_league = tablas['league']
        df_country = tablas['country']

        # 2) Atributos por temporada (medianas/modas)
        print("\n⏳ Preparando atributos de la temporada 2015-2016...")
        df_attr_temp, cols_num, cols_text = _preparar_atributos_temporada(df_attributes)

        # 3) Asignar equipo, liga y país (último partido 2016)
        print("⏳ Asignando Equipo, Liga y País (último partido de 2016)...")
        df_attr_enriquecido = _asignar_equipo_liga_pais(df_attr_temp, df_match, df_team, df_league, df_country)

        # 4) Normalización de tipos y NaNs
        print("⏳ Normalizando tipos numéricos y completando NaNs...")
        df_attr_limpio = _limpiar_tipos_y_nans(df_attr_enriquecido)

        # 5) Merge final con Player y guardado CSV
        print("\n🧩 Uniendo Player con atributos enriquecidos...")
        df_consolidado = _unir_player_con_atributos(df_player, df_attr_limpio)
        df_consolidado.to_csv(RUTA_ABSOLUTA_CSV, index=False)
        print(f"\n💾 DataFrame limpio y consolidado guardado como '{CSV_FILE_NAME}'.")
        df_final = df_consolidado

    # Info de procesamiento
    _load_info['processing_time'] = time.time() - start_time
    _load_info['timestamp'] = time.time()

    # 6) SQL en memoria para análisis ad-hoc
    print("\n--- Preparando Motor SQL en Memoria para Análisis ---")
    _registrar_sql_en_memoria(df_final)
    print("✅ DataFrame consolidado registrado como tabla 'jugadores_2016'.")

    return df_final


def load_data():
    """
    Función principal para cargar datos de jugadores de fútbol 2016.
    Retorna un DataFrame con información consolidada de jugadores, atributos, equipos, ligas y países,
    y también retorna la información de carga.
    """
    df = main()
    # Devolvemos tanto el DataFrame como la información de carga
    return df, _load_info.copy()


def get_data_info(df):
    """
    Extrae información resumida del DataFrame de jugadores de fútbol.
    
    Returns:
        dict: Diccionario con estadísticas clave del dataset.
    """
    info = {
        'total_jugadores': len(df),
        'total_equipos': df['team_long_name'].nunique() if 'team_long_name' in df.columns else 0,
        'total_ligas': df['league_name'].nunique() if 'league_name' in df.columns else 0,
        'rating_promedio': df['overall_rating'].mean() if 'overall_rating' in df.columns else 0,
        'rating_max': df['overall_rating'].max() if 'overall_rating' in df.columns else 0,
        'edad_promedio': None,
        'altura_promedio': None,
        'peso_promedio': None,
        'pase_promedio': None,
        'altura_porteros': None,
        'altura_jugadores': None,
    }
    
    # Calcular edad promedio si tenemos birthday
    if 'birthday' in df.columns:
        from datetime import datetime
        df_temp = df.copy()
        df_temp['birthday'] = pd.to_datetime(df_temp['birthday'], errors='coerce')
        df_temp['edad'] = (pd.Timestamp('2016-12-31') - df_temp['birthday']).dt.days / 365.25
        info['edad_promedio'] = df_temp['edad'].mean()
    
    # Calcular altura promedio (ya está en cm)
    if 'height' in df.columns:
        info['altura_promedio'] = df['height'].mean()
    
    # Calcular peso promedio - CONVERTIR DE LIBRAS A KILOGRAMOS
    if 'weight' in df.columns:
        info['peso_promedio'] = df['weight'].mean() * 0.453592  # Conversión libras → kg
    
    # Calcular habilidad de pase promedio (más útil que velocidad)
    if 'short_passing' in df.columns:
        info['pase_promedio'] = df['short_passing'].mean()
    
    # Calcular altura de porteros vs jugadores de campo
    if 'height' in df.columns and 'gk_reflexes' in df.columns:
        # Porteros tienen gk_reflexes > 0 (no nulo y mayor que 0)
        porteros = df[df['gk_reflexes'] > 10]  # Umbral para identificar porteros
        jugadores = df[df['gk_reflexes'] <= 10]
        
        if len(porteros) > 0:
            info['altura_porteros'] = porteros['height'].mean()
        if len(jugadores) > 0:
            info['altura_jugadores'] = jugadores['height'].mean()
    
    return info


def get_load_info():
    """
    Obtiene información sobre el proceso de carga del CSV.
    
    Returns:
        dict: Diccionario con información de carga (si ya existía, tiempo de procesamiento, etc.)
    """
    return _load_info.copy()


def delete_csv():
    """
    Elimina el archivo CSV si existe.
    
    Returns:
        bool: True si se eliminó correctamente, False si no existía o hubo error.
    """
    try:
        if os.path.exists(RUTA_ABSOLUTA_CSV):
            os.remove(RUTA_ABSOLUTA_CSV)
            print(f"🗑️ Archivo CSV eliminado: {RUTA_ABSOLUTA_CSV}")
            return True
        else:
            print(f"⚠️ El archivo CSV no existe: {RUTA_ABSOLUTA_CSV}")
            return False
    except Exception as e:
        print(f"❌ Error al eliminar CSV: {e}")
        return False


# if __name__ == "__main__":
#     main()