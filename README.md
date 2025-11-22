# Sistema de Gestión de Asistencias y Horas Extras

Aplicación de escritorio para la gestión integral de empleados, turnos y asistencias. Diseñada para automatizar el cálculo de horas extras y facilitar la administración de personal mediante una interfaz intuitiva y potentes herramientas de importación.

---

## 👥 Autores

Proyecto desarrollado para el curso de **Gestión de Datos e Información** por:

*   **Butrón Prieto Alexis Gonzalo**
*   **Calla Torres Cristian Fernando**
*   **Loaiza Cruz Joaquin Armando**
*   **Sánchez Velasquez Adriano Alessio**

---

## ⭐ Características Destacadas

*   **Gestión de Empleados:** CRUD completo con asignación de áreas y centros de coste.
*   **Control de Asistencias:** Registro manual y masivo de entradas y salidas.
*   **Cálculo Automático:** Clasificación de horas extras (25%, 35%, 100%) según normativa.
*   **Importación Inteligente:** Carga masiva desde Excel (`.xlsx`) con detección de formatos.
---

## 🚀 Descarga y Ejecución (Recomendado)

Para usar la aplicación **NO necesitas instalar Python** ni configurar entornos. Solo descarga el ejecutable.

### 📥 Paso 1: Descargar
Ve a la sección de **Releases** en GitHub y descarga la última versión:

**[👉 Descargar SistemaGestionBD.exe (Última Versión)](https://github.com/JoaquinLoaizaUCSM/aplicativo_bd/releases/latest)**

### ▶️ Paso 2: Ejecutar
1.  Ubica el archivo `SistemaGestionBD.exe` descargado.
2.  Asegúrate de tener el archivo de configuración `db_config.json` en la misma carpeta (si es la primera vez, el programa lo creará).
3.  ¡Doble clic y listo!

---

## 🗄️ Base de Datos y Scripts de Prueba

Para que la aplicación funcione, necesitas una base de datos MySQL. Hemos incluido scripts listos para usar en la carpeta `Scripts SQL`.

### 📂 Contenido de `Scripts SQL`

Ubicación: [`/Scripts SQL`](./Scripts%20SQL)

1.  **`Crear_DB.sql`**: Crea la estructura base de la base de datos `sobretiempos`.
2.  **`Procedures.sql`**: Instala todos los procedimientos almacenados necesarios para la lógica del negocio.
3.  **`Triggers.sql`**: Configura los disparadores para automatizaciones en la BD.
4.  **`Datos_trabajadores.sql`**: (Opcional) Carga datos de prueba para verificar el funcionamiento.

### ⚙️ Configuración Rápida de la BD

1.  Abre tu gestor de MySQL (Workbench, DBeaver, etc.).
2.  Ejecuta los scripts en el siguiente orden:
    1.  `Crear_DB.sql`
    2.  `Procedures.sql`
    3.  `Triggers.sql`
3.  (Opcional) Ejecuta `Datos_trabajadores.sql` si quieres tener empleados de prueba.
4.  Al abrir la aplicación, ingresa tus credenciales de MySQL cuando se te soliciten.

---

## 💻 Instalación para Desarrolladores (Código Fuente)

Si deseas modificar el código o contribuir:

### Requisitos
*   Python 3.10+
*   MySQL Server 8.0

### Pasos
1.  Clonar el repositorio.
2.  Crear entorno virtual: `python -m venv .venv`
3.  Instalar dependencias: `pip install -r requirements.txt`
4.  Ejecutar: `python main.py`

O usa el script automático en Windows:
```powershell
.\run_app.ps1
```

---

## 📄 Licencia
Este software es de uso privado y académico.