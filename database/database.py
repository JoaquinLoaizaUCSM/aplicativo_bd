"""
Módulo de conexión a la base de datos
Autor: [Tu nombre]
Fecha: 2025-11-07
Descripción: Gestiona la conexión directa a MySQL sin usar frameworks.
             Permite ejecutar procedimientos almacenados y consultas SQL nativas.
"""

import mysql.connector
from mysql.connector import Error
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
from typing import Optional, Tuple, List, Any, Union, Dict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Clase para gestionar la conexión a la base de datos MySQL de forma nativa.
    No utiliza ORMs ni frameworks, solo conexión directa.
    """
    
    def __init__(self, config: Union[Dict[str, Any], str], port: Optional[int] = None, 
                 user: Optional[str] = None, password: Optional[str] = None, database: Optional[str] = None):
        """
        Inicializa los parámetros de conexión.
        
        Args:
            config: Diccionario con configuración o string con host
            port: Puerto de conexión (opcional si config es dict)
            user: Usuario de la base de datos (opcional si config es dict)
            password: Contraseña del usuario (opcional si config es dict)
            database: Nombre de la base de datos (opcional si config es dict)
        """
        if isinstance(config, dict):
            self.host = config.get('host', 'localhost')
            self.port = config.get('port', 3306)
            self.user = config.get('user', 'root')
            self.password = config.get('password', '')
            self.database = config.get('database', '')
        else:
            self.host = config
            self.port = port or 3306
            self.user = user or 'root'
            self.password = password or ''
            self.database = database or ''
        
        self.connection: Optional[Union[MySQLConnectionAbstract, PooledMySQLConnection]] = None
        self.cursor = None
        
    def connect(self) -> Tuple[bool, str]:
        """
        Establece la conexión con la base de datos.
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Construir kwargs de forma dinámica para evitar pasar parámetros
            # no soportados por algunas versiones del conector (p.ej. 'collation').
            conn_kwargs = {
                'host': self.host,
                'port': self.port,
                'user': self.user,
                'password': self.password,
                'charset': 'utf8mb4'
            }

            # Incluir la base de datos solo si fue proporcionada
            if self.database:
                conn_kwargs['database'] = self.database

            self.connection = mysql.connector.connect(**conn_kwargs)
            
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                logger.info(f"Conectado a MySQL Server versión {db_info}")
                return True, f"Conexión exitosa a MySQL Server {db_info}"
            else:
                return False, "No se pudo establecer la conexión"
                
        except Error as e:
            error_msg = f"Error al conectar a MySQL: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def disconnect(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        try:
            if self.cursor:
                try:
                    self.cursor.close()
                except Exception:
                    pass
                self.cursor = None
                
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Conexión a MySQL cerrada")
            self.connection = None
        except Error as e:
            logger.error(f"Error al cerrar la conexión: {str(e)}")
            # Asegurar que se limpie la referencia aunque falle el cierre
            self.connection = None
    
    def test_connection(self) -> Optional[Dict[str, Any]]:
        """
        Prueba la conexión a la base de datos y retorna información del servidor.
        
        Returns:
            Dict con información del servidor o None si falla
        """
        info: Dict[str, Any] = {}
        cursor = None
        try:
            success, message = self.connect()
            if not success:
                return None
            
            # Verificar que la conexión no sea None
            if self.connection is None:
                return None
            
            # Obtener información de la base de datos
            cursor = self.connection.cursor(dictionary=True)  # type: ignore
            
            # Información del servidor
            cursor.execute("SELECT VERSION() AS version")
            version_info = cursor.fetchone()
            if version_info and isinstance(version_info, dict):
                info['version'] = version_info.get('version', 'N/A')
            
            # Nombre de la base de datos actual
            cursor.execute("SELECT DATABASE() AS db_name")
            db_info = cursor.fetchone()
            if db_info and isinstance(db_info, dict):
                info['database'] = db_info.get('db_name', 'N/A')
            
            # Usuario conectado
            cursor.execute("SELECT USER() AS user_name")
            user_info = cursor.fetchone()
            if user_info and isinstance(user_info, dict):
                info['user_name'] = user_info.get('user_name', 'N/A')
            
            # Character set
            cursor.execute("SELECT @@character_set_database AS character_set")
            charset_info = cursor.fetchone()
            if charset_info and isinstance(charset_info, dict):
                info['character_set'] = charset_info.get('character_set', 'N/A')
            
            # Connection ID
            cursor.execute("SELECT CONNECTION_ID() AS connection_id")
            conn_info = cursor.fetchone()
            if conn_info and isinstance(conn_info, dict):
                info['connection_id'] = conn_info.get('connection_id', 'N/A')
            
            if cursor:
                cursor.close()
            self.disconnect()
            
            return info
            
        except Error as e:
            error_msg = f"Error en la prueba de conexión: {str(e)}"
            logger.error(error_msg)
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            try:
                self.disconnect()
            except:
                pass
            return None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Tuple[bool, str, List[Any]]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Tuple[bool, str, List]: (éxito, mensaje, resultados)
        """
        results: List[Any] = []
        try:
            success, message = self.connect()
            if not success or self.connection is None:
                return False, message, results
            
            cursor = self.connection.cursor(dictionary=True)  # type: ignore
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = list(cursor.fetchall())
            cursor.close()
            self.disconnect()
            
            return True, f"Consulta ejecutada exitosamente. {len(results)} registros obtenidos.", results
            
        except Error as e:
            error_msg = f"Error al ejecutar la consulta: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, results
    
    def execute_procedure(self, procedure_name: str, params: Optional[tuple] = None) -> Tuple[bool, str, List[Any]]:
        """
        Ejecuta un procedimiento almacenado.
        
        Args:
            procedure_name: Nombre del procedimiento almacenado
            params: Parámetros del procedimiento (opcional)
            
        Returns:
            Tuple[bool, str, List]: (éxito, mensaje, resultados)
        """
        results: List[Any] = []
        try:
            success, message = self.connect()
            if not success or self.connection is None:
                return False, message, results
            
            cursor = self.connection.cursor(dictionary=True)  # type: ignore
            
            # Llamar al procedimiento almacenado
            if params:
                cursor.callproc(procedure_name, params)
            else:
                cursor.callproc(procedure_name)
            
            # Obtener resultados
            for result in cursor.stored_results():  # type: ignore
                results.extend(list(result.fetchall()))
            
            self.connection.commit()
            cursor.close()
            self.disconnect()
            
            return True, f"Procedimiento '{procedure_name}' ejecutado exitosamente.", results
            
        except Error as e:
            error_msg = f"Error al ejecutar el procedimiento: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, results
    
    def execute_insert(self, query: str, params: Optional[tuple] = None) -> Tuple[bool, str, int]:
        """
        Ejecuta una consulta INSERT y retorna el ID del registro insertado.
        
        Args:
            query: Consulta INSERT a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Tuple[bool, str, int]: (éxito, mensaje, last_id)
        """
        last_id = 0
        try:
            success, message = self.connect()
            if not success or self.connection is None:
                return False, message, last_id
            
            cursor = self.connection.cursor()  # type: ignore
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            last_id = int(cursor.lastrowid) if cursor.lastrowid else 0
            
            cursor.close()
            self.disconnect()
            
            return True, f"Registro insertado exitosamente. ID: {last_id}", last_id
            
        except Error as e:
            error_msg = f"Error al insertar: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, last_id
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> Tuple[bool, str, int]:
        """
        Ejecuta una consulta UPDATE y retorna el número de filas afectadas.
        
        Args:
            query: Consulta UPDATE a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Tuple[bool, str, int]: (éxito, mensaje, rows_affected)
        """
        rows_affected = 0
        try:
            success, message = self.connect()
            if not success or self.connection is None:
                return False, message, rows_affected
            
            cursor = self.connection.cursor()  # type: ignore
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            rows_affected = cursor.rowcount
            
            cursor.close()
            self.disconnect()
            
            return True, f"Actualización exitosa. {rows_affected} filas afectadas.", rows_affected
            
        except Error as e:
            error_msg = f"Error al actualizar: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, rows_affected
    
    def execute_delete(self, query: str, params: Optional[tuple] = None) -> Tuple[bool, str, int]:
        """
        Ejecuta una consulta DELETE y retorna el número de filas eliminadas.
        
        Args:
            query: Consulta DELETE a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Tuple[bool, str, int]: (éxito, mensaje, rows_deleted)
        """
        rows_deleted = 0
        try:
            success, message = self.connect()
            if not success or self.connection is None:
                return False, message, rows_deleted
            
            cursor = self.connection.cursor()  # type: ignore
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            rows_deleted = cursor.rowcount
            
            cursor.close()
            self.disconnect()
            
            return True, f"Eliminación exitosa. {rows_deleted} filas eliminadas.", rows_deleted
            
        except Error as e:
            error_msg = f"Error al eliminar: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, rows_deleted
