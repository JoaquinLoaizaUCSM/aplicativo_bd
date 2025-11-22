<#
PowerShell script para activar el entorno virtual del proyecto y ejecutar la aplicación
Uso:
  .\run_app.ps1
Opciones:
  -Crea un virtualenv en .venv si no existe
  -Activa el venv (dot-sourcing) y instala requirements
  -Ejecuta main.py
#>

# Buscar posibles nombres de venv
$venvCandidates = @('.venv','venv','env')
$activate = $null
foreach ($v in $venvCandidates) {
    $act = Join-Path $v 'Scripts\Activate.ps1'
    if (Test-Path $act) { $activate = $act; break }
}

if (-not $activate) {
    Write-Host "No se encontró virtualenv. Creando .venv..."
    python -m venv .venv
    $activate = Join-Path '.venv' 'Scripts\Activate.ps1'
}

if (Test-Path $activate) {
    Write-Host "Activando entorno virtual: $activate"
    # Dot-source para aplicar la activación al contexto actual del script
    . $activate
} else {
    Write-Warning "No se encontró el script de activación ($activate). Continuando sin activar venv."
}

# Instalar dependencias si existe requirements.txt
if (Test-Path 'requirements.txt') {
    Write-Host "Verificando dependencias..."
    pip install -r requirements.txt | Out-Null
}

# Ejecutar la aplicación
Write-Host "Iniciando la aplicación (main.py)..."
python main.py
