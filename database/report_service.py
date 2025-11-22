"""
Servicio para generación de reportes
Proporciona funciones para generar reportes de horas extras y estadísticas
"""

from typing import Optional, List, Dict, Any
from database.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class ReportService:
    """Servicio para generación de reportes"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio con una conexión a la base de datos.
        
        Args:
            db_connection: Instancia de DatabaseConnection
        """
        self.db = db_connection
    
    def get_overtime_by_employee(self, fecha_inicio: str, fecha_fin: str,
                                codigo_empleado: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Genera reporte de horas extras por empleado.
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            codigo_empleado: Código de empleado específico (opcional)
            
        Returns:
            Lista con reporte de horas extras o None si hay error
        """
        try:
            params: tuple[Any, ...]
            if codigo_empleado:
                params = (fecha_inicio, fecha_fin, codigo_empleado)
            else:
                params = (fecha_inicio, fecha_fin, None)
            success, message, results = self.db.execute_procedure("sp_reporte_horas_extras_empleado", params)
            if success:
                return results
            logger.error(f"Error al generar reporte: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al generar reporte: {str(e)}")
            return None
    
    def get_overtime_by_cost_center(self, fecha_inicio: str, fecha_fin: str) -> Optional[List[Dict[str, Any]]]:
        """
        Genera reporte de horas extras por centro de coste.
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            
        Returns:
            Lista con reporte por centro de coste o None si hay error
        """
        try:
            params = (fecha_inicio, fecha_fin)
            success, message, results = self.db.execute_procedure("sp_reporte_horas_extras_centro_coste", params)
            if success:
                return results
            logger.error(f"Error al generar reporte: {message}")
            return None
        except Exception as e:
            logger.error(f"Excepción al generar reporte: {str(e)}")
            return None
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene estadísticas generales para el dashboard.
        
        Returns:
            Diccionario con estadísticas o None si hay error
        """
        try:
            stats = {}
            
            # 1. Asistencias de Hoy
            query_today = "SELECT COUNT(*) as count FROM reporte_asistencia WHERE fecha = CURDATE()"
            success, _, res_today = self.db.execute_query(query_today)
            stats['asistencias_hoy'] = res_today[0]['count'] if success and res_today else 0
            
            # 2. Faltas de Hoy (Total Empleados - Asistencias Hoy)
            # Primero obtenemos total empleados
            query_emp = "SELECT COUNT(*) as count FROM empleados"
            success, _, res_emp = self.db.execute_query(query_emp)
            total_emp = res_emp[0]['count'] if success and res_emp else 0
            stats['total_empleados'] = total_emp
            stats['faltas_hoy'] = max(0, total_emp - stats['asistencias_hoy'])
            
            # 3. Registros Incompletos (Sin marca de salida hoy)
            # Asumimos que si marca_salida es NULL o '00:00:00' está incompleto
            query_inc = "SELECT COUNT(*) as count FROM reporte_asistencia WHERE fecha = CURDATE() AND (marca_salida IS NULL OR marca_salida = '00:00:00')"
            success, _, res_inc = self.db.execute_query(query_inc)
            stats['incompletos_hoy'] = res_inc[0]['count'] if success and res_inc else 0
            
            # 4. Llegadas Tarde (Hoy)
            # Compara marca_entrada con hora_entrada del turno (con 5 min de tolerancia por ejemplo)
            query_late = """
                SELECT COUNT(*) as count 
                FROM reporte_asistencia ra 
                JOIN turnos t ON ra.codigo_turno = t.codigo_turno 
                WHERE ra.fecha = CURDATE() 
                AND ra.marca_entrada > ADDTIME(t.hora_entrada, '00:05:00')
            """
            success, _, res_late = self.db.execute_query(query_late)
            stats['tardanzas_hoy'] = res_late[0]['count'] if success and res_late else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Excepción al obtener estadísticas: {str(e)}")
            return None
