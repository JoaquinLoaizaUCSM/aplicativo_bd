-- Procedimientos almacenados para el aplicativo GDI
-- Ejecutar este archivo sobre la base de datos `sobretiempos`

USE sobretiempos;

DELIMITER $$

-- sp_listar_asistencias: devuelve todo el registro de asistencias con joins a empleados y turnos.
DROP PROCEDURE IF EXISTS sp_listar_asistencias $$
CREATE PROCEDURE sp_listar_asistencias()
BEGIN
    SELECT 
        ra.fecha AS fecha_asistencia,
        ra.dia,
        ra.codigo_empleado,
        COALESCE(e.nombre, '') AS nombre_empleado,
        ra.codigo_turno,
        COALESCE(t.hora_entrada, '') AS turno_entrada,
        COALESCE(t.hora_salida, '') AS turno_salida,
        ra.marca_entrada,
        ra.marca_salida,
        ROUND(COALESCE(TIMESTAMPDIFF(MINUTE, ra.marca_entrada, ra.marca_salida) / 60, 0), 2) AS horas_trabajadas,
        COALESCE(ra.H25, 0) AS horas_25,
        COALESCE(ra.H35, 0) AS horas_35,
        COALESCE(ra.H100, 0) AS horas_100,
        (COALESCE(ra.H25, 0) + COALESCE(ra.H35, 0) + COALESCE(ra.H100, 0)) AS total_horas_extras
    FROM reporte_asistencia ra
    LEFT JOIN empleados e ON e.codigo = ra.codigo_empleado
    LEFT JOIN turnos t ON t.codigo_turno = ra.codigo_turno
    ORDER BY ra.fecha DESC, nombre_empleado;
END $$

-- sp_filtrar_asistencias: aplica filtros opcionales (término, fechas, empleado) antes de listar asistencias.
DROP PROCEDURE IF EXISTS sp_filtrar_asistencias $$
CREATE PROCEDURE sp_filtrar_asistencias(
    IN p_termino VARCHAR(100),
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_codigo_empleado VARCHAR(20)
)
BEGIN
    SELECT 
        ra.fecha AS fecha_asistencia,
        ra.dia,
        ra.codigo_empleado,
        COALESCE(e.nombre, '') AS nombre_empleado,
        ra.codigo_turno,
        COALESCE(t.hora_entrada, '') AS turno_entrada,
        COALESCE(t.hora_salida, '') AS turno_salida,
        ra.marca_entrada,
        ra.marca_salida,
        ROUND(COALESCE(TIMESTAMPDIFF(MINUTE, ra.marca_entrada, ra.marca_salida) / 60, 0), 2) AS horas_trabajadas,
        COALESCE(ra.H25, 0) AS horas_25,
        COALESCE(ra.H35, 0) AS horas_35,
        COALESCE(ra.H100, 0) AS horas_100,
        (COALESCE(ra.H25, 0) + COALESCE(ra.H35, 0) + COALESCE(ra.H100, 0)) AS total_horas_extras
    FROM reporte_asistencia ra
    LEFT JOIN empleados e ON e.codigo = ra.codigo_empleado
    LEFT JOIN turnos t ON t.codigo_turno = ra.codigo_turno
    WHERE (p_termino IS NULL OR p_termino = '' OR ra.codigo_empleado LIKE p_termino OR e.nombre LIKE p_termino)
      AND (p_fecha_inicio IS NULL OR ra.fecha >= p_fecha_inicio)
      AND (p_fecha_fin IS NULL OR ra.fecha <= p_fecha_fin)
      AND (p_codigo_empleado IS NULL OR p_codigo_empleado = '' OR ra.codigo_empleado = p_codigo_empleado)
    ORDER BY ra.fecha DESC, nombre_empleado;
END $$

-- sp_insertar_asistencia: inserta una nueva fila de asistencia y devuelve un mensaje del resultado.
DROP PROCEDURE IF EXISTS sp_insertar_asistencia $$
CREATE PROCEDURE sp_insertar_asistencia(
    IN p_fecha DATE,
    IN p_codigo_empleado VARCHAR(20),
    IN p_codigo_turno VARCHAR(10),
    IN p_dia VARCHAR(15),
    IN p_marca_entrada TIME,
    IN p_marca_salida TIME
)
BEGIN
    DECLARE v_rows INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        INSERT INTO reporte_asistencia (
            fecha, codigo_empleado, codigo_turno, dia,
            marca_entrada, marca_salida, H25, H35, H100
        ) VALUES (
            p_fecha, p_codigo_empleado, p_codigo_turno, p_dia,
            p_marca_entrada, p_marca_salida, 0, 0, 0
        );
        SET v_rows = ROW_COUNT();
    COMMIT;

    SELECT v_rows AS affected_rows,
           CASE WHEN v_rows > 0 THEN 'Asistencia registrada correctamente'
                ELSE 'No se insertó ningún registro de asistencia' END AS message;
END $$

-- sp_actualizar_asistencia: actualiza turno, marcas y horas extras de un registro existente.
DROP PROCEDURE IF EXISTS sp_actualizar_asistencia $$
CREATE PROCEDURE sp_actualizar_asistencia(
    IN p_fecha DATE,
    IN p_codigo_empleado VARCHAR(20),
    IN p_codigo_turno VARCHAR(10),
    IN p_dia VARCHAR(15),
    IN p_marca_entrada TIME,
    IN p_marca_salida TIME,
    IN p_h25 DECIMAL(6,2),
    IN p_h35 DECIMAL(6,2),
    IN p_h100 DECIMAL(6,2)
)
BEGIN
    DECLARE v_rows INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        UPDATE reporte_asistencia
        SET codigo_turno = p_codigo_turno,
            dia = p_dia,
            marca_entrada = p_marca_entrada,
            marca_salida = p_marca_salida,
            H25 = p_h25,
            H35 = p_h35,
            H100 = p_h100
        WHERE fecha = p_fecha AND codigo_empleado = p_codigo_empleado;
        SET v_rows = ROW_COUNT();
    COMMIT;

    SELECT v_rows AS affected_rows,
           CASE WHEN v_rows > 0 THEN 'Asistencia actualizada correctamente'
                ELSE 'No se encontró el registro de asistencia solicitado' END AS message;
END $$

-- sp_eliminar_asistencia: elimina una asistencia específica por fecha y código de empleado.
DROP PROCEDURE IF EXISTS sp_eliminar_asistencia $$
CREATE PROCEDURE sp_eliminar_asistencia(
    IN p_fecha DATE,
    IN p_codigo_empleado VARCHAR(20)
)
BEGIN
    DECLARE v_rows INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        DELETE FROM reporte_asistencia
        WHERE fecha = p_fecha AND codigo_empleado = p_codigo_empleado;
        SET v_rows = ROW_COUNT();
    COMMIT;

    SELECT v_rows AS affected_rows,
           CASE WHEN v_rows > 0 THEN 'Asistencia eliminada correctamente'
                ELSE 'No se encontró el registro a eliminar' END AS message;
END $$

-- sp_listar_empleados: lista todos los empleados con su área, centro de coste y subdivisión.
DROP PROCEDURE IF EXISTS sp_listar_empleados $$
CREATE PROCEDURE sp_listar_empleados()
BEGIN
    SELECT 
        e.codigo,
        COALESCE(e.nombre, '') AS nombre,
        COALESCE(e.dni, '') AS dni,
        COALESCE(NULLIF(e.puesto_area, ''), '') AS puesto,
        COALESCE(a.unidad_organizativa, '') AS unidad_organizativa,
        COALESCE(cc.centro_coste, '') AS centro_coste,
        COALESCE(cc.codigo_centroCoste, e.Codigo_CentroCoste, '') AS codigo_centro_coste,
        COALESCE(e.subdivision, '') AS subdivision
    FROM empleados e
    LEFT JOIN area a ON e.puesto_area = a.puesto
    LEFT JOIN centro_coste cc ON e.Codigo_CentroCoste = cc.codigo_centroCoste
    ORDER BY e.codigo;
END $$

-- sp_buscar_empleados: busca empleados por código, nombre o DNI utilizando un patrón LIKE.
DROP PROCEDURE IF EXISTS sp_buscar_empleados $$
CREATE PROCEDURE sp_buscar_empleados(
    IN p_termino VARCHAR(100)
)
BEGIN
    SELECT 
        e.codigo,
        COALESCE(e.nombre, '') AS nombre,
        COALESCE(e.dni, '') AS dni,
        COALESCE(NULLIF(e.puesto_area, ''), '') AS puesto,
        COALESCE(a.unidad_organizativa, '') AS unidad_organizativa,
        COALESCE(cc.centro_coste, '') AS centro_coste,
        COALESCE(cc.codigo_centroCoste, e.Codigo_CentroCoste, '') AS codigo_centro_coste,
        COALESCE(e.subdivision, '') AS subdivision
    FROM empleados e
    LEFT JOIN area a ON e.puesto_area = a.puesto
    LEFT JOIN centro_coste cc ON e.Codigo_CentroCoste = cc.codigo_centroCoste
    WHERE p_termino IS NULL OR p_termino = ''
        OR e.codigo LIKE p_termino
        OR e.nombre LIKE p_termino
        OR e.dni LIKE p_termino
    ORDER BY e.codigo;
END $$

-- sp_obtener_empleado: retorna un único empleado identificado por su código.
DROP PROCEDURE IF EXISTS sp_obtener_empleado $$
CREATE PROCEDURE sp_obtener_empleado(
    IN p_codigo VARCHAR(20)
)
BEGIN
    SELECT 
        e.codigo,
        COALESCE(e.nombre, '') AS nombre,
        COALESCE(e.dni, '') AS dni,
        COALESCE(NULLIF(e.puesto_area, ''), '') AS puesto,
        COALESCE(a.unidad_organizativa, '') AS unidad_organizativa,
        COALESCE(cc.centro_coste, '') AS centro_coste,
        COALESCE(cc.codigo_centroCoste, e.Codigo_CentroCoste, '') AS codigo_centro_coste,
        COALESCE(e.subdivision, '') AS subdivision
    FROM empleados e
    LEFT JOIN area a ON e.puesto_area = a.puesto
    LEFT JOIN centro_coste cc ON e.Codigo_CentroCoste = cc.codigo_centroCoste
    WHERE e.codigo = p_codigo
    LIMIT 1;
END $$

-- sp_insertar_empleado: crea un empleado y asegura la operación dentro de una transacción.
DROP PROCEDURE IF EXISTS sp_insertar_empleado $$
CREATE PROCEDURE sp_insertar_empleado(
    IN p_codigo VARCHAR(20),
    IN p_nombre VARCHAR(150),
    IN p_dni VARCHAR(20),
    IN p_puesto VARCHAR(150),
    IN p_codigo_centro_coste VARCHAR(50),
    IN p_subdivision VARCHAR(150)
)
BEGIN
    DECLARE v_rows INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        INSERT INTO empleados (
            codigo, nombre, dni, puesto_area, Codigo_CentroCoste, subdivision
        ) VALUES (
            p_codigo, p_nombre, p_dni, p_puesto, p_codigo_centro_coste, p_subdivision
        );
        SET v_rows = ROW_COUNT();
    COMMIT;

    SELECT v_rows AS affected_rows,
           CASE WHEN v_rows > 0 THEN CONCAT('Empleado ', p_codigo, ' creado correctamente')
                ELSE 'No se insertó ningún registro de empleado' END AS message;
END $$

-- sp_actualizar_empleado: modifica los campos principales del empleado especificado.
DROP PROCEDURE IF EXISTS sp_actualizar_empleado $$
CREATE PROCEDURE sp_actualizar_empleado(
    IN p_codigo VARCHAR(20),
    IN p_nombre VARCHAR(150),
    IN p_dni VARCHAR(20),
    IN p_puesto VARCHAR(150),
    IN p_codigo_centro_coste VARCHAR(50),
    IN p_subdivision VARCHAR(150)
)
BEGIN
    DECLARE v_rows INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        UPDATE empleados
        SET nombre = p_nombre,
            dni = p_dni,
            puesto_area = p_puesto,
            Codigo_CentroCoste = p_codigo_centro_coste,
            subdivision = p_subdivision
        WHERE codigo = p_codigo;
        SET v_rows = ROW_COUNT();
    COMMIT;

    SELECT v_rows AS affected_rows,
           CASE WHEN v_rows > 0 THEN 'Empleado actualizado correctamente'
                ELSE 'No se encontró el empleado solicitado' END AS message;
END $$

-- sp_eliminar_empleado: elimina un empleado y todas sus asistencias relacionadas.
DROP PROCEDURE IF EXISTS sp_eliminar_empleado $$
CREATE PROCEDURE sp_eliminar_empleado(
    IN p_codigo VARCHAR(20)
)
BEGIN
    DECLARE v_rows INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        DELETE FROM reporte_asistencia WHERE codigo_empleado = p_codigo;
        DELETE FROM empleados WHERE codigo = p_codigo;
        SET v_rows = ROW_COUNT();
    COMMIT;

    SELECT v_rows AS affected_rows,
           CASE WHEN v_rows > 0 THEN CONCAT('Empleado ', p_codigo, ' eliminado correctamente')
                ELSE 'No se encontró el empleado solicitado' END AS message;
END $$

-- sp_generar_codigo_empleado: calcula el siguiente código incremental con prefijo 'E'.
DROP PROCEDURE IF EXISTS sp_generar_codigo_empleado $$
CREATE PROCEDURE sp_generar_codigo_empleado()
BEGIN
    SELECT CONCAT('E', LPAD(COALESCE(MAX(CAST(SUBSTRING(codigo, 2) AS UNSIGNED)), 0) + 1, 5, '0')) AS codigo
    FROM empleados;
END $$

-- sp_listar_centros_coste: devuelve el catálogo completo de centros de coste.
DROP PROCEDURE IF EXISTS sp_listar_centros_coste $$
CREATE PROCEDURE sp_listar_centros_coste()
BEGIN
    SELECT 
        codigo_centroCoste AS codigo,
        centro_coste AS nombre
    FROM centro_coste
    ORDER BY centro_coste;
END $$

-- sp_listar_areas: lista todos los puestos y su unidad organizativa.
DROP PROCEDURE IF EXISTS sp_listar_areas $$
CREATE PROCEDURE sp_listar_areas()
BEGIN
    SELECT 
        puesto,
        unidad_organizativa
    FROM area
    ORDER BY unidad_organizativa, puesto;
END $$

-- sp_listar_turnos: entrega el catálogo de turnos con sus horarios de entrada y salida.
DROP PROCEDURE IF EXISTS sp_listar_turnos $$
CREATE PROCEDURE sp_listar_turnos()
BEGIN
    SELECT 
        codigo_turno,
        hora_entrada,
        hora_salida
    FROM turnos
    ORDER BY hora_entrada;
END $$

-- sp_reporte_horas_extras_empleado: consolida horas extras por empleado en un rango de fechas.
DROP PROCEDURE IF EXISTS sp_reporte_horas_extras_empleado $$
CREATE PROCEDURE sp_reporte_horas_extras_empleado(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_codigo_empleado VARCHAR(20)
)
BEGIN
    SELECT 
        e.codigo AS codigo_empleado,
        e.nombre AS nombre_empleado,
        COALESCE(NULLIF(e.puesto_area, ''), '') AS puesto,
        COALESCE(SUM(ra.H25), 0) AS total_horas_25,
        COALESCE(SUM(ra.H35), 0) AS total_horas_35,
        COALESCE(SUM(ra.H100), 0) AS total_horas_100,
        COALESCE(SUM(ra.H25 + ra.H35 + ra.H100), 0) AS total_horas_extras
    FROM empleados e
    LEFT JOIN reporte_asistencia ra ON e.codigo = ra.codigo_empleado
        AND ra.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    WHERE p_codigo_empleado IS NULL OR p_codigo_empleado = '' OR e.codigo = p_codigo_empleado
    GROUP BY e.codigo, e.nombre, e.puesto_area
    HAVING total_horas_extras > 0
    ORDER BY total_horas_extras DESC;
END $$

-- sp_reporte_horas_extras_centro_coste: resume horas extras agrupadas por centro de coste.
DROP PROCEDURE IF EXISTS sp_reporte_horas_extras_centro_coste $$
CREATE PROCEDURE sp_reporte_horas_extras_centro_coste(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    SELECT 
        cc.codigo_centroCoste AS codigo_centro_coste,
        cc.centro_coste AS nombre_centro_coste,
        COUNT(DISTINCT e.codigo) AS total_empleados,
        COALESCE(SUM(ra.H25), 0) AS total_horas_25,
        COALESCE(SUM(ra.H35), 0) AS total_horas_35,
        COALESCE(SUM(ra.H100), 0) AS total_horas_100,
        COALESCE(SUM(ra.H25 + ra.H35 + ra.H100), 0) AS total_horas_extras
    FROM centro_coste cc
    LEFT JOIN empleados e ON cc.codigo_centroCoste = e.Codigo_CentroCoste
    LEFT JOIN reporte_asistencia ra ON e.codigo = ra.codigo_empleado
        AND ra.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    GROUP BY cc.codigo_centroCoste, cc.centro_coste
    HAVING total_horas_extras > 0
    ORDER BY total_horas_extras DESC;
END $$

-- sp_obtener_estadisticas: obtiene totales de empleados, asistencias recientes y horas extras.
DROP PROCEDURE IF EXISTS sp_obtener_estadisticas $$
CREATE PROCEDURE sp_obtener_estadisticas()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM empleados) AS total_empleados,
        (SELECT COUNT(*) FROM reporte_asistencia WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) AS asistencias_mes,
        (SELECT COALESCE(SUM(H25 + H35 + H100), 0) FROM reporte_asistencia WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) AS horas_extras_mes;
END $$

DELIMITER ;
