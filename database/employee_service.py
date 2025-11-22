"""Servicio para gestión de empleados mediante procedimientos almacenados."""

from typing import Optional, List, Dict, Any
from database.database import DatabaseConnection
from database.operation_result import OperationResult, OperationStatus
import logging

logger = logging.getLogger(__name__)


class EmployeeService:
    """Servicio para operaciones CRUD de empleados basado en procedimientos almacenados"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Inicializa el servicio con una conexión a la base de datos."""
        self.db = db_connection
    
    def get_all_employees(self) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene todos los empleados con información completa.
        
        Returns:
            Lista de empleados o None si hay error
        """
        try:
            success, message, results = self.db.execute_procedure("sp_listar_empleados")
            if success:
                return results
            logger.error(f"Error al listar empleados: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al listar empleados: {str(e)}")
            return None
    
    def search_employees(self, search_term: str) -> Optional[List[Dict[str, Any]]]:
        """
        Busca empleados por código, nombre o DNI.
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de empleados encontrados o None si hay error
        """
        try:
            params = (f"%{search_term}%",)
            success, message, results = self.db.execute_procedure("sp_buscar_empleados", params)
            if success:
                return results
            logger.error(f"Error al buscar empleados: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al buscar empleados: {str(e)}")
            return None
    
    def get_employee_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un empleado por su código.
        
        Args:
            code: Código del empleado
            
        Returns:
            Diccionario con datos del empleado o None si no existe
        """
        try:
            success, message, results = self.db.execute_procedure("sp_obtener_empleado", (code,))
            if success and results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Excepción al obtener empleado: {str(e)}")
            return None
    
    def create_employee(
        self,
        codigo: str,
        nombre: str,
        dni: str,
        puesto: str,
        codigo_centro_coste: str,
        subdivision: Optional[str] = None,
    ) -> OperationResult:
        """
        Crea un nuevo empleado.
        
        Args:
            codigo: Código del empleado (ej: E00023)
            nombre: Nombre completo
            dni: DNI (8 dígitos)
            puesto: Puesto/área del empleado
            codigo_centro_coste: Código del centro de coste
            subdivision: Subdivisión
            
        Returns:
            OperationResult con el estado de la operación
        """
        try:
            params = (codigo, nombre, dni, puesto, codigo_centro_coste, subdivision)
            success, message, results = self.db.execute_procedure("sp_insertar_empleado", params)
            if success:
                return self._build_operation_result(
                    results,
                    success_message=f"Empleado {codigo} creado correctamente",
                    empty_action_message="No se insertó ningún registro de empleado",
                )
            return self._operation_from_error(
                message,
                duplicate_message="Ya existe un empleado con el mismo código o DNI.",
            )
        except Exception as e:
            error_msg = f"Error al crear empleado: {str(e)}"
            logger.error(error_msg)
            return OperationResult.failure(OperationStatus.ERROR, error_msg)
    
    def update_employee(self, codigo: str, nombre: str, dni: str,
                       puesto: str, codigo_centro_coste: str,
                       subdivision: Optional[str] = None) -> OperationResult:
        """
        Actualiza un empleado existente.
        
        Args:
            codigo: Código del empleado
            nombre: Nombre completo
            dni: DNI (8 dígitos)
            puesto: Puesto/área del empleado
            codigo_centro_coste: Código del centro de coste
            subdivision: Subdivisión (opcional)
            
        Returns:
            OperationResult con el estado de la operación
        """
        try:
            params = (codigo, nombre, dni, puesto, codigo_centro_coste, subdivision)
            success, message, results = self.db.execute_procedure("sp_actualizar_empleado", params)
            if success:
                return self._build_operation_result(
                    results,
                    success_message="Empleado actualizado correctamente",
                    empty_action_message="No se encontró el empleado solicitado",
                )
            return self._operation_from_error(message)
        except Exception as e:
            error_msg = f"Error al actualizar empleado: {str(e)}"
            logger.error(error_msg)
            return OperationResult.failure(OperationStatus.ERROR, error_msg)
    
    def delete_employee(self, codigo: str) -> OperationResult:
        """
        Elimina un empleado y sus registros de asistencia.
        
        Args:
            codigo: Código del empleado a eliminar
            
        Returns:
            OperationResult con el estado de la operación
        """
        try:
            success, message, results = self.db.execute_procedure("sp_eliminar_empleado", (codigo,))
            if success:
                return self._build_operation_result(
                    results,
                    success_message=f"Empleado {codigo} eliminado correctamente",
                    empty_action_message="No se encontró el empleado solicitado",
                )
            return self._operation_from_error(message)
        except Exception as e:
            error_msg = f"Error al eliminar empleado: {str(e)}"
            logger.error(error_msg)
            return OperationResult.failure(OperationStatus.ERROR, error_msg)
    
    def generate_employee_code(self) -> Optional[str]:
        """
        Genera el siguiente código de empleado disponible.
        
        Returns:
            Código generado (ej: E00023) o None si hay error
        """
        try:
            success, message, results = self.db.execute_procedure("sp_generar_codigo_empleado")
            if success and results:
                return results[0].get('codigo')
            return None
        except Exception as e:
            logger.error(f"Error al generar código: {str(e)}")
            return None

    @staticmethod
    def _is_duplicate_error(message: str) -> bool:
        lowered = message.lower()
        return "1062" in lowered or "duplicate" in lowered or "duplicado" in lowered

    def _operation_from_error(
        self,
        message: str,
        duplicate_message: Optional[str] = None,
    ) -> OperationResult:
        if self._is_duplicate_error(message):
            return OperationResult.failure(
                OperationStatus.DUPLICATE,
                duplicate_message or "Ya existe un registro con la misma información.",
            )
        return OperationResult.failure(OperationStatus.ERROR, message)

    @staticmethod
    def _classify_message(message: str) -> OperationStatus:
        lowered = message.lower()
        if "no se encontr" in lowered:
            return OperationStatus.NOT_FOUND
        if "no se insert" in lowered:
            return OperationStatus.VALIDATION_ERROR
        if "duplic" in lowered:
            return OperationStatus.DUPLICATE
        return OperationStatus.ERROR

    def _build_operation_result(
        self,
        results: Optional[List[Dict[str, Any]]],
        success_message: str,
        empty_action_message: str,
    ) -> OperationResult:
        if not results:
            return OperationResult.failure(
                OperationStatus.ERROR,
                "El procedimiento no retornó información para determinar el resultado.",
            )

        payload = results[0]
        affected = int(payload.get('affected_rows', 0) or 0)
        message = payload.get('message') or (success_message if affected > 0 else empty_action_message)

        if affected > 0:
            return OperationResult.success(message)

        status = self._classify_message(message)
        if status == OperationStatus.ERROR and message == empty_action_message:
            status = OperationStatus.NOT_FOUND
        return OperationResult.failure(status, message)
