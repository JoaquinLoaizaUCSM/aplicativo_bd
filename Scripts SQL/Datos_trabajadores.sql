-- Script V2 para poblar la base de datos con datos masivos de prueba
-- Incluye 4 turnos y más de 50 registros de asistencia para validar cálculos H25, H35, H100.

USE sobretiempos;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Limpiar tablas
TRUNCATE TABLE reporte_asistencia;
TRUNCATE TABLE empleados;
TRUNCATE TABLE turnos;
TRUNCATE TABLE area;
TRUNCATE TABLE centro_coste;

SET FOREIGN_KEY_CHECKS = 1;

-- 2. Insertar Centros de Coste
INSERT INTO centro_coste (codigo_centroCoste, centro_coste) VALUES
('CC-LIMA', 'Sede Central Lima'),
('CC-AREQ', 'Planta Arequipa'),
('CC-TRUJ', 'Sucursal Trujillo'),
('CC-CUSC', 'Oficina Cusco'),
('CC-PIUR', 'Almacén Piura');

-- 3. Insertar Áreas
INSERT INTO area (puesto, unidad_organizativa) VALUES
('Desarrollador Senior', 'Tecnología'),
('Analista de BD', 'Tecnología'),
('Contador General', 'Finanzas'),
('Asistente Administrativo', 'Administración'),
('Operario de Producción', 'Operaciones'),
('Supervisor de Planta', 'Operaciones'),
('Vendedor Senior', 'Comercial'),
('Jefe de Logística', 'Logística');

-- 4. Insertar Turnos (4 Tipos)
-- T01: Administrativo (08:00 - 17:00)
-- T02: Planta Mañana (07:00 - 16:00)
-- T03: Planta Tarde (14:00 - 22:00)
-- T04: Nocturno (22:00 - 06:00) -> Nota: El cálculo de horas extras nocturnas puede requerir lógica especial si cruza medianoche,
-- pero para este ejemplo asumiremos que marca_salida es la hora real de salida del turno.
INSERT INTO turnos (codigo_turno, hora_entrada, hora_salida) VALUES
('T01', '08:00:00', '17:00:00'),
('T02', '07:00:00', '16:00:00'),
('T03', '14:00:00', '22:00:00'),
('T04', '22:00:00', '06:00:00');

-- 5. Insertar Empleados (10 Empleados)
INSERT INTO empleados (codigo, nombre, dni, puesto_area, Codigo_CentroCoste, subdivision) VALUES
('E0001', 'Juan Perez', '10000001', 'Desarrollador Senior', 'CC-LIMA', 'Lima'),
('E0002', 'Maria Rodriguez', '10000002', 'Contador General', 'CC-AREQ', 'Arequipa'),
('E0003', 'Carlos Mamani', '10000003', 'Operario de Producción', 'CC-CUSC', 'Cusco'),
('E0004', 'Ana Flores', '10000004', 'Vendedor Senior', 'CC-TRUJ', 'Trujillo'),
('E0005', 'Luis Sanchez', '10000005', 'Supervisor de Planta', 'CC-PIUR', 'Piura'),
('E0006', 'Sofia Lopez', '10000006', 'Asistente Administrativo', 'CC-LIMA', 'Lima'),
('E0007', 'Miguel Torres', '10000007', 'Analista de BD', 'CC-LIMA', 'Lima'),
('E0008', 'Elena Quispe', '10000008', 'Operario de Producción', 'CC-AREQ', 'Arequipa'),
('E0009', 'Jorge Diaz', '10000009', 'Jefe de Logística', 'CC-PIUR', 'Piura'),
('E0010', 'Rosa Silva', '10000010', 'Vendedor Senior', 'CC-CUSC', 'Cusco');

-- 6. Insertar Asistencias Masivas
-- Generaremos registros para la semana del 17 al 23 de Noviembre de 2024.
-- 17 Nov = Domingo (H100)
-- 18-22 Nov = Lunes a Viernes (Normal)
-- 23 Nov = Sábado (Normal)

-- ========================================================================================
-- DOMINGO 17 NOV (H100)
-- ========================================================================================
-- E0003 trabaja en domingo (3 horas extra) -> H100=3.00
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES
('2024-11-17', 'E0003', 'T02', 'Domingo', '07:00:00', '19:00:00');

-- E0008 trabaja en domingo (5 horas extra) -> H100=5.00
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES
('2024-11-17', 'E0008', 'T02', 'Domingo', '07:00:00', '21:00:00');

-- ========================================================================================
-- LUNES 18 NOV
-- ========================================================================================
-- E0001: 2h extra (H25=2)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0001', 'T01', 'Lunes', '07:55:00', '19:00:00');
-- E0002: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0002', 'T01', 'Lunes', '08:00:00', '17:00:00');
-- E0003: 1h extra (H25=1)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0003', 'T02', 'Lunes', '06:50:00', '17:00:00');
-- E0004: 4h extra (H25=2, H35=2)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0004', 'T01', 'Lunes', '08:00:00', '21:00:00');
-- E0005: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0005', 'T03', 'Lunes', '14:00:00', '22:00:00');
-- E0006: 30 min extra (H25=0.5)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0006', 'T01', 'Lunes', '08:00:00', '17:30:00');
-- E0007: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0007', 'T01', 'Lunes', '08:00:00', '17:00:00');
-- E0008: 1.5h extra (H25=1.5)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0008', 'T02', 'Lunes', '07:00:00', '17:30:00');
-- E0009: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0009', 'T01', 'Lunes', '08:00:00', '17:00:00');
-- E0010: 3h extra (H25=2, H35=1)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-18', 'E0010', 'T01', 'Lunes', '08:00:00', '20:00:00');

-- ========================================================================================
-- MARTES 19 NOV
-- ========================================================================================
-- E0001: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0001', 'T01', 'Martes', '08:00:00', '17:00:00');
-- E0002: 5h extra (H25=2, H35=3)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0002', 'T01', 'Martes', '08:00:00', '22:00:00');
-- E0003: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0003', 'T02', 'Martes', '07:00:00', '16:00:00');
-- E0004: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0004', 'T01', 'Martes', '08:00:00', '17:00:00');
-- E0005: 2h extra (H25=2) - Turno Tarde (Salida 22:00 -> 24:00)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0005', 'T03', 'Martes', '14:00:00', '23:59:59'); -- Simulado casi medianoche
-- E0006: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0006', 'T01', 'Martes', '08:00:00', '17:00:00');
-- E0007: 1h extra (H25=1)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0007', 'T01', 'Martes', '08:00:00', '18:00:00');
-- E0008: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0008', 'T02', 'Martes', '07:00:00', '16:00:00');
-- E0009: 2.5h extra (H25=2, H35=0.5)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0009', 'T01', 'Martes', '08:00:00', '19:30:00');
-- E0010: Puntual
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-19', 'E0010', 'T01', 'Martes', '08:00:00', '17:00:00');

-- ========================================================================================
-- MIERCOLES 20 NOV
-- ========================================================================================
-- Todos puntuales excepto E0001 y E0005
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0001', 'T01', 'Miercoles', '08:00:00', '18:00:00'); -- 1h extra
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0002', 'T01', 'Miercoles', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0003', 'T02', 'Miercoles', '07:00:00', '16:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0004', 'T01', 'Miercoles', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0005', 'T03', 'Miercoles', '14:00:00', '23:00:00'); -- 1h extra
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0006', 'T01', 'Miercoles', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0007', 'T01', 'Miercoles', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0008', 'T02', 'Miercoles', '07:00:00', '16:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0009', 'T01', 'Miercoles', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-20', 'E0010', 'T01', 'Miercoles', '08:00:00', '17:00:00');

-- ========================================================================================
-- JUEVES 21 NOV
-- ========================================================================================
-- Variados
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0001', 'T01', 'Jueves', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0002', 'T01', 'Jueves', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0003', 'T02', 'Jueves', '07:00:00', '18:00:00'); -- 2h extra
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0004', 'T01', 'Jueves', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0005', 'T03', 'Jueves', '14:00:00', '22:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0006', 'T01', 'Jueves', '08:00:00', '19:00:00'); -- 2h extra
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0007', 'T01', 'Jueves', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0008', 'T02', 'Jueves', '07:00:00', '16:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0009', 'T01', 'Jueves', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-21', 'E0010', 'T01', 'Jueves', '08:00:00', '20:00:00'); -- 3h extra

-- ========================================================================================
-- VIERNES 22 NOV
-- ========================================================================================
-- Todos salen temprano (sin extras)
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0001', 'T01', 'Viernes', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0002', 'T01', 'Viernes', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0003', 'T02', 'Viernes', '07:00:00', '16:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0004', 'T01', 'Viernes', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0005', 'T03', 'Viernes', '14:00:00', '22:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0006', 'T01', 'Viernes', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0007', 'T01', 'Viernes', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0008', 'T02', 'Viernes', '07:00:00', '16:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0009', 'T01', 'Viernes', '08:00:00', '17:00:00');
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES ('2024-11-22', 'E0010', 'T01', 'Viernes', '08:00:00', '17:00:00');

-- ========================================================================================
-- DOMINGO 24 NOV (H100) - PRUEBA FINAL
-- ========================================================================================
-- E0001 trabaja domingo completo (9h) -> H100=9.00? No, solo extras.
-- Si trabaja en domingo, ¿todo es extra o solo lo que pasa del turno?
-- Asumiremos que si tiene turno asignado, las horas extras son las que pasan de la salida.
-- PERO, si es domingo, usualmente es descanso. Si trabaja, ¿todo es extra?
-- El trigger actual calcula: (Salida Real - Salida Turno).
-- Si el turno es de 8 a 17, y sale a las 19, son 2 horas extras.
-- Si es domingo, esas 2 horas son al 100%.
-- Para que tenga muchas horas H100, debe quedarse mucho después de su turno.
INSERT INTO reporte_asistencia (fecha, codigo_empleado, codigo_turno, dia, marca_entrada, marca_salida) VALUES
('2024-11-24', 'E0001', 'T01', 'Domingo', '08:00:00', '20:00:00'); -- 3h extra al 100%

SELECT 'Datos V2 insertados correctamente. Se generaron 50+ registros.' AS Mensaje;
SELECT * FROM reporte_asistencia ORDER BY fecha DESC;
