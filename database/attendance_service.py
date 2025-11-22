"""Servicio para gestión de asistencias respaldado por procedimientos almacenados."""

from typing import Optional, List, Dict, Any
from database.database import DatabaseConnection
from database.operation_result import OperationResult, OperationStatus
import logging

logger = logging.getLogger(__name__)


class AttendanceService:
    """Servicio para operaciones CRUD de asistencias mediante procedimientos almacenados"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio con una conexión a la base de datos.
        
        Args:
            db_connection: Instancia de DatabaseConnection
        """
        self.db = db_connection
    
    def get_all_attendance(self) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene todos los registros de asistencia.
        
        Returns:
            Lista de asistencias o None si hay error
        """
        try:
            success, message, results = self.db.execute_procedure("sp_listar_asistencias")
            if success:
                return results
            logger.error(f"Error al listar asistencias: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al listar asistencias: {str(e)}")
            return None
    
    def filter_attendance(self, search_term: Optional[str] = None,
                         fecha_inicio: Optional[str] = None,
                         fecha_fin: Optional[str] = None,
                         codigo_empleado: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Filtra registros de asistencia según criterios.
        
        Args:
            search_term: Término de búsqueda (código o nombre)
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            codigo_empleado: Código de empleado específico
            
        Returns:
            Lista de asistencias filtradas o None si hay error
        """
        try:
            params = (
                f"%{search_term}%" if search_term else None,
                fecha_inicio,
                fecha_fin,
                codigo_empleado,
            )
            success, message, results = self.db.execute_procedure("sp_filtrar_asistencias", params)
            if success:
                return results
            logger.error(f"Error al filtrar asistencias: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al filtrar asistencias: {str(e)}")
            return None
    
    def create_attendance(
        self,
        fecha: str,
        codigo_empleado: str,
        codigo_turno: str,
        dia: str,
        marca_entrada: Optional[str] = None,
        marca_salida: Optional[str] = None,
    ) -> OperationResult:
        """
        Crea un nuevo registro de asistencia.
        Las horas extras se calculan automáticamente mediante trigger.
        
        Args:
            fecha: Fecha de asistencia (YYYY-MM-DD)
            codigo_empleado: Código del empleado
            codigo_turno: Código del turno (M01, M02, T01, N01)
            dia: Nombre del día (Lunes, Martes, etc.)
            marca_entrada: Hora de entrada (HH:MM:SS) opcional
            marca_salida: Hora de salida (HH:MM:SS) opcional
            
        Returns:
            OperationResult con el estado de la operación
        """
        try:
            params = (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida)
            success, message, results = self.db.execute_procedure("sp_insertar_asistencia", params)
            if success:
                return self._build_operation_result(
                    results,
                    success_message="Asistencia registrada correctamente",
                    empty_action_message="No se insertó ningún registro de asistencia",
                )
            return self._operation_from_error(
                message,
                duplicate_message="Ya existe una asistencia con la misma fecha para este empleado.",
            )
        except Exception as e:
            error_msg = f"Error al crear asistencia: {str(e)}"
            logger.error(error_msg)
            return OperationResult.failure(OperationStatus.ERROR, error_msg)
    
    def update_attendance(self, fecha: str, codigo_empleado: str, codigo_turno: str,
                         dia: str, marca_entrada: Optional[str], marca_salida: Optional[str],
                         h25: float, h35: float, h100: float) -> OperationResult:
        """
        Actualiza un registro de asistencia existente.
        
        Args:
            fecha: Fecha de asistencia (YYYY-MM-DD)
            codigo_empleado: Código del empleado
            codigo_turno: Código del turno
            dia: Nombre del día
            marca_entrada: Hora de entrada (HH:MM:SS)
            marca_salida: Hora de salida (HH:MM:SS)
            h25: Horas extras al 25%
            h35: Horas extras al 35%
            h100: Horas extras al 100%
            
        Returns:
            OperationResult con el estado de la operación
        """
        try:
            params = (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida, h25, h35, h100)
            success, message, results = self.db.execute_procedure("sp_actualizar_asistencia", params)
            if success:
                return self._build_operation_result(
                    results,
                    success_message="Asistencia actualizada correctamente",
                    empty_action_message="No se encontró el registro de asistencia solicitado",
                )
            return self._operation_from_error(message)
        except Exception as e:
            error_msg = f"Error al actualizar asistencia: {str(e)}"
            logger.error(error_msg)
            return OperationResult.failure(OperationStatus.ERROR, error_msg)
    
    def delete_attendance(self, fecha: str, codigo_empleado: str) -> OperationResult:
        """
        Elimina un registro de asistencia.
        
        Args:
            fecha: Fecha de asistencia (YYYY-MM-DD)
            codigo_empleado: Código del empleado
            
        Returns:
            OperationResult con el estado de la operación
        """
        try:
            success, message, results = self.db.execute_procedure(
                "sp_eliminar_asistencia",
                (fecha, codigo_empleado),
            )
            if success:
                return self._build_operation_result(
                    results,
                    success_message="Asistencia eliminada correctamente",
                    empty_action_message="No se encontró el registro a eliminar",
                )
            return self._operation_from_error(message)
        except Exception as e:
            error_msg = f"Error al eliminar asistencia: {str(e)}"
            logger.error(error_msg)
            return OperationResult.failure(OperationStatus.ERROR, error_msg)

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
                duplicate_message or "Ya existe un registro con los mismos datos.",
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
        affected = int(payload.get("affected_rows", 0) or 0)
        message = payload.get("message") or (success_message if affected > 0 else empty_action_message)

        if affected > 0:
            return OperationResult.success(message)

        status = self._classify_message(message)
        # Si el mensaje no permitió clasificar, degrade a error genérico
        if status == OperationStatus.ERROR and message == empty_action_message:
            status = OperationStatus.NOT_FOUND
        return OperationResult.failure(status, message)
