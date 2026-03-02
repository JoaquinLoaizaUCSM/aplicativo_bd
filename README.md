# 📊 Sistema de Gestión de Sobretiempos

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-00758F?style=for-the-badge&logo=mysql&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-Academic-green?style=for-the-badge)

> **Especializado en el cálculo, clasificación y reporte de horas extras.**

Esta aplicación de escritorio está diseñada específicamente para **gestionar y calcular sobretiempos**, procesando registros de asistencia para generar reportes precisos de horas extras (25%, 35%, 100%) según la normativa, facilitando así el trabajo de planilla.

---

## 👥 Autores

Proyecto desarrollado para el curso de **Gestión de Datos e Información** por:

| Integrante | Rol |
| :--- | :--- |
| **Sánchez Velasquez Adriano Alessio** | Lider-Desarrollador |
| **Butrón Prieto Alexis Gonzalo** | Desarrollador |
| **Calla Torres Cristian Fernando** | Desarrollador |
| **Loaiza Cruz Joaquin Armando** | Desarrollador |


---

## ⭐ Características Destacadas

### ⏱️ Cálculo de Sobretiempos
*   **Clasificación Automática:** Algoritmos precisos para identificar y clasificar horas extras (25%, 35%, 100%) basándose en las marcaciones.
*   **Reglas de Negocio:** Aplicación de normativas vigentes para el cálculo de beneficios.

### 📊 Reportes y Exportación
*   **Reportes Detallados:** Generación de reportes listos para el área de nóminas/planilla.
*   **Visualización de Datos:** Tablas claras para revisar el detalle de horas por trabajador.

### 🔄 Gestión de Datos
*   **Importación de Marcaciones:** Carga masiva de registros de entrada/salida desde Excel (`.xlsx`) para su procesamiento.
*   **Maestro de Trabajadores:** Mantenimiento de la información necesaria de los empleados para el cálculo.

---

## 🚀 Descarga y Ejecución

¡No necesitas instalar Python! Hemos empaquetado todo para ti.

### 📥 Paso 1: Descargar
Obtén la última versión estable desde nuestra sección de lanzamientos:

[![Descargar v1.0](https://img.shields.io/badge/Descargar-SistemaGestionBD.exe-blueviolet?style=for-the-badge&logo=github)](https://github.com/JoaquinLoaizaUCSM/aplicativo_bd/releases/latest)

### ▶️ Paso 2: Ejecutar
1.  Ubica el archivo `SistemaGestionBD.exe`.
2.  Ejecútalo con doble clic.
3.  Ingresa tus credenciales de base de datos cuando se soliciten.

> [!NOTE]
> El archivo `db_config.json` se creará automáticamente la primera vez para guardar tu configuración de conexión.

---

## 💻 Instalación para Desarrolladores

Si deseas contribuir o modificar el código fuente, sigue estos pasos:

### Requisitos Previos
*   **Python 3.10** o superior.
*   **MySQL Server 8.0** en ejecución.

### Configuración del Entorno

1.  **Clonar el repositorio**
    ```bash
    git clone https://github.com/JoaquinLoaizaUCSM/aplicativo_bd.git
    cd aplicativo_bd
    ```

2.  **Crear entorno virtual**
    ```bash
    python -m venv .venv
    ```

3.  **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**
    ```bash
    python main.py
    ```
    *O usa el script automático en Windows:*
    ```powershell
    .\run_app.ps1
    ```

---

## 📄 Licencia
Este software fue desarrollado con fines académicos y de uso privado.
