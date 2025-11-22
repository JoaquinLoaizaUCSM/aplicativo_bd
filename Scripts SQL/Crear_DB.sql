DROP TABLE IF EXISTS reporte_asistencia;
DROP TABLE IF EXISTS empleados;
DROP TABLE IF EXISTS area;
DROP TABLE IF EXISTS centro_coste;
DROP TABLE IF EXISTS turnos;

-- Tabla Centro de Coste
CREATE TABLE centro_coste (
  codigo_centroCoste CHAR(8) PRIMARY KEY,
  centro_coste VARCHAR(50) NOT NULL
);

-- Tabla Area
CREATE TABLE area (
  puesto CHAR(80) PRIMARY KEY,
  unidad_organizativa VARCHAR(50) NOT NULL
);

-- Tabla Turno
CREATE TABLE turnos (
  codigo_turno CHAR(3) PRIMARY KEY,
  hora_entrada TIME NOT NULL,
  hora_salida TIME NOT NULL
);

-- Tabla Empleado
CREATE TABLE empleados (
  codigo CHAR(6) PRIMARY KEY,
  puesto_area CHAR(80) NOT NULL,
  Codigo_CentroCoste CHAR(8) NOT NULL,
  nombre VARCHAR(80) NOT NULL,
  dni CHAR(8) UNIQUE NOT NULL,
  subdivision VARCHAR(100),
  FOREIGN KEY (Codigo_CentroCoste) REFERENCES centro_coste(codigo_centroCoste),
  FOREIGN KEY (puesto_area) REFERENCES area(puesto)
);


CREATE INDEX idx_nombre_empleado ON empleados(nombre);

-- Tabla Reporte_Asistencia
CREATE TABLE reporte_asistencia (
  fecha DATE,
  codigo_empleado CHAR(6),
  codigo_turno CHAR(3) NOT NULL,
  dia VARCHAR(15) NOT NULL,
  marca_entrada TIME NULL,
  marca_salida TIME NULL,
  H25 DECIMAL(5,2) DEFAULT 0,
  H35 DECIMAL(5,2) DEFAULT 0,
  H100 DECIMAL(5,2) DEFAULT 0,
  PRIMARY KEY (fecha, codigo_empleado),
  FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
  FOREIGN KEY (codigo_turno) REFERENCES turnos(codigo_turno)
);
