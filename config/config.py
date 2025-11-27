"""
Módulo de configuración de la base de datos
Autor: [Tu nombre]
Fecha: 2025-11-07
Descripción: Contiene las credenciales y parámetros de conexión a la base de datos MySQL
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


if getattr(sys, 'frozen', False):
    # Si estamos en el ejecutable, usar la carpeta del ejecutable
    CONFIG_DIR = Path(sys.executable).parent
else:
    # Si estamos en desarrollo, usar la carpeta del archivo actual
    CONFIG_DIR = Path(__file__).resolve().parent

DB_CONFIG_FILE = CONFIG_DIR / 'db_config.json'


# Configuración de la base de datos (valores por defecto)
DEFAULT_DB_CONFIG: Dict[str, Any] = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',  # Cambiar por tu contraseña
    'database': 'sobretiempos',  # Base de datos del sistema de asistencias
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}


def _normalize_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    """Combina los valores recibidos con los predeterminados de forma segura."""
    normalized = DEFAULT_DB_CONFIG.copy()
    for key in DEFAULT_DB_CONFIG:
        if key not in raw_config:
            continue
        value = raw_config[key]
        if key == 'port':
            try:
                port_val = int(value)
                if 1 <= port_val <= 65535:
                    normalized[key] = port_val
            except (TypeError, ValueError):
                continue
        elif value is not None:
            normalized[key] = value
    return normalized


def _write_db_config(config: Dict[str, Any]) -> None:
    DB_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def _load_db_config_from_disk() -> Dict[str, Any]:
    """Lee la configuración desde disco o crea el archivo con valores por defecto."""
    if DB_CONFIG_FILE.exists():
        try:
            with open(DB_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return _normalize_config(data)
        except Exception:
            pass  # Se usará la configuración por defecto si falla la lectura

    # Si no existe, crear archivo con valores por defecto
    _write_db_config(DEFAULT_DB_CONFIG)
    return DEFAULT_DB_CONFIG.copy()


DB_CONFIG: Dict[str, Any] = _load_db_config_from_disk()


def get_db_config() -> Dict[str, Any]:
    """Retorna una copia de la configuración actual de base de datos."""
    return DB_CONFIG.copy()


def save_db_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Persiste la configuración de base de datos y devuelve la versión normalizada."""
    global DB_CONFIG
    DB_CONFIG = _normalize_config(new_config)
    try:
        _write_db_config(DB_CONFIG)
    except Exception:
        # Si falla la escritura, mantener la config en memoria pero notificar mediante excepción
        raise
    return DB_CONFIG.copy()

# Configuración de la aplicación
APP_CONFIG = {
    'title': 'Sistema de Gestión de Base de Datos',
    'app_name': 'Empresa de Bebidas',
    'version': '1.0',
    'width': 1400,
    'height': 800,
    'resizable': True
}

# Configuración de colores y estilos
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'light': '#ecf0f1',
    'dark': '#34495e'
}
