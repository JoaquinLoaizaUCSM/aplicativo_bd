# Sistema de Gestión de Asistencias y Horas Extras

Este proyecto es una aplicación de escritorio desarrollada en Python para la gestión integral de empleados, turnos y asistencias. Permite el cálculo automático de horas extras, importación masiva de datos desde Excel y generación de reportes.

## Características

*   **Gestión de Empleados:** CRUD completo de empleados con asignación de áreas y centros de coste.
*   **Control de Asistencias:** Registro manual y masivo de entradas y salidas.
*   **Cálculo de Horas Extras:** Cálculo automático de horas trabajadas y clasificación de horas extras (25%, 35%, 100%) según la normativa.
*   **Importación Inteligente:** Módulo avanzado para importar reportes de asistencia desde Excel (`.xlsx`), con detección automática de formatos y creación de turnos faltantes.
*   **Reportes:** Visualización de estadísticas y exportación de datos.
*   **Base de Datos:** Uso de MySQL con procedimientos almacenados para la lógica de negocio.

## 🛠️ Requisitos del Sistema

*   **Sistema Operativo:** Windows 10/11.
*   **Base de Datos:** MySQL Server 8.0.
*   **Para versión código fuente:** Python 3.10+ y librerías (`mysql-connector-python`, `openpyxl`).
*   **Para versión ejecutable:** No requiere Python instalado.

## 🚀 Ejecución (Versión Portable / Ejecutable)

### 📥 Descargar el Ejecutable

Puedes descargar la última versión del ejecutable directamente desde la página de releases de GitHub:

**[👉 Descargar SistemaGestionBD.exe desde Releases](https://github.com/JoaquinLoaizaUCSM/aplicativo_bd/releases/latest)**

En la sección de "Assets" encontrarás el archivo `SistemaGestionBD.exe` listo para usar sin necesidad de instalar Python ni dependencias.

### ▶️ Cómo Ejecutar

Si dispone de la versión compilada (`.exe`):
1.  Descarga el archivo `SistemaGestionBD.exe` desde la página de releases (enlace arriba).
2.  Asegúrese de que el archivo `db_config.json` esté junto al ejecutable.
3.  Ejecute `SistemaGestionBD.exe`.

## 💻 Instalación y Configuración (Código Fuente)

### 1. Clonar el Repositorio
Descarga el código fuente en tu equipo local.

### 2. Configurar Base de Datos
1.  Asegúrate de tener MySQL Server en ejecución.
2.  Crea la base de datos `sobretiempos`.
3.  Ejecuta el script SQL ubicado en `database/procedures.sql` para crear las tablas y procedimientos almacenados necesarios.

### 3. Configurar Credenciales
Edita el archivo `config/config.py` (o crea uno basado en `config/config.example.py`) con tus credenciales de MySQL:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'TU_CONTRASEÑA',
    'database': 'sobretiempos'
}
```

### 4. Ejecutar la Aplicación
Para facilitar la ejecución, se incluye un script de PowerShell que configura automáticamente el entorno virtual e instala las dependencias.

**Opción A: Usando el script automático (Recomendado)**
Abre PowerShell en la carpeta del proyecto y ejecuta:
```powershell
.\run_app.ps1
```

**Opción B: Manualmente**
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

## 📂 Estructura del Proyecto

```
aplicativo_bd/
├── config/                 # Configuración de la aplicación
│   ├── config.py           # Credenciales de BD
│   └── db_config.json      # Configuración persistente
├── database/               # Capa de acceso a datos
│   ├── attendance_service.py # Lógica de asistencias
│   ├── employee_service.py   # Lógica de empleados
│   ├── procedures.sql        # Script SQL de la BD
│   └── ...
├── gui/                    # Interfaz Gráfica (Tkinter)
│   ├── main_window.py      # Ventana principal
│   ├── import_view.py      # Vista de importación Excel
│   └── ...
├── main.py                 # Punto de entrada
├── run_app.ps1             # Script de ejecución automática
└── requirements.txt        # Dependencias del proyecto
```

## � Guía de Uso

### Importación de Asistencias
1.  Ve a la sección **Importar**.
2.  Selecciona "Importar Asistencias (Excel)".
3.  Carga tu archivo `Reporte_AsistenciaDetallado.xlsx`.
4.  El sistema detectará automáticamente:
    *   Códigos de empleado (en cabecera o columnas).
    *   Fechas y Horas.
    *   Turnos (creándolos si no existen).

### Gestión de Empleados
*   Usa la pestaña **Empleados** para agregar, editar o dar de baja personal.
*   Los códigos de empleado se generan automáticamente (E00001, etc.) o pueden ingresarse manualmente.

## 🤝 Contribución
Proyecto desarrollado para el curso de Gestión de Datos e Información.

## 📄 Licencia
Este software es de uso privado y académico.