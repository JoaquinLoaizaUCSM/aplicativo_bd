"""
Servicio para obtener datos de referencia
Proporciona funciones para obtener centros de coste, áreas, turnos, etc.
"""

from typing import Optional, List, Dict, Any
from database.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class ReferenceService:
    """Servicio para datos de referencia"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio con una conexión a la base de datos.
        
        Args:
            db_connection: Instancia de DatabaseConnection
        """
        self.db = db_connection
        self._cost_centers_cache: Optional[List[Dict[str, Any]]] = None
        self._areas_cache: Optional[List[Dict[str, Any]]] = None
        self._shifts_cache: Optional[List[Dict[str, Any]]] = None

    def clear_cache(self):
        """Limpia la caché de datos de referencia."""
        self._cost_centers_cache = None
        self._areas_cache = None
        self._shifts_cache = None
    
    def get_cost_centers(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene todos los centros de coste.
        
        Args:
            force_refresh: Si es True, ignora la caché y consulta la BD.
            
        Returns:
            Lista de centros de coste o None si hay error
        """
        if self._cost_centers_cache is not None and not force_refresh:
            return self._cost_centers_cache

        try:
            success, message, results = self.db.execute_procedure("sp_listar_centros_coste")
            if success:
                self._cost_centers_cache = results
                return results
            logger.error(f"Error al listar centros de coste: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al listar centros de coste: {str(e)}")
            return None
    
    def get_areas(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene todas las áreas/puestos.
        
        Args:
            force_refresh: Si es True, ignora la caché y consulta la BD.
            
        Returns:
            Lista de áreas o None si hay error
        """
        if self._areas_cache is not None and not force_refresh:
            return self._areas_cache

        try:
            success, message, results = self.db.execute_procedure("sp_listar_areas")
            if success:
                self._areas_cache = results
                return results
            logger.error(f"Error al listar áreas: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al listar áreas: {str(e)}")
            return None
    
    def get_shifts(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene todos los turnos.
        
        Args:
            force_refresh: Si es True, ignora la caché y consulta la BD.
            
        Returns:
            Lista de turnos o None si hay error
        """
        if self._shifts_cache is not None and not force_refresh:
            return self._shifts_cache

        try:
            success, message, results = self.db.execute_procedure("sp_listar_turnos")
            if success:
                self._shifts_cache = results
                return results
            logger.error(f"Error al listar turnos: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al listar turnos: {str(e)}")
            return None
