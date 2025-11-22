# Asegurar que estamos en el directorio del script
Set-Location $PSScriptRoot

Write-Host "Iniciando proceso de construcción..."

# Limpiar carpetas anteriores
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

# Ejecutar PyInstaller
# Usamos python -m PyInstaller para asegurar que usa el módulo instalado en el entorno actual
python -m PyInstaller SistemaGestionBD.spec

# Verificar si se creó el ejecutable
if (Test-Path "dist/SistemaGestionBD.exe") {
    Write-Host "Ejecutable creado exitosamente."
    
    # Copiar archivos adicionales
    Write-Host "Copiando archivos de configuración..."
    
    # Copiar db_config.json si existe
    if (Test-Path "config/db_config.json") {
        Copy-Item "config/db_config.json" "dist/db_config.json"
    }

    Write-Host "Proceso completado. El ejecutable está en la carpeta 'dist'."
    Write-Host "Puede distribuir la carpeta 'dist' completa."
} else {
    Write-Host "Error: No se pudo crear el ejecutable."
}
