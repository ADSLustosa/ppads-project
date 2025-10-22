# run.ps1 - setup + run usando Python do VSCode/Path
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

function Get-Py {
    $cands = @(
        @("$env:LocalAppData\Microsoft\WindowsApps\python.exe"),
        @("$env:LocalAppData\Programs\Python\Python312\python.exe"),
        @("$env:LocalAppData\Python\pythoncore-3.14-64\python.exe"),
        @("python"),
        @("py","-3.14"),
        @("py","-3.13"),
        @("py","-3.12"),
        @("py","-3.11"),
        @("py","-3")
    )
    foreach ($cand in $cands) {
        try { & $cand[0] $cand[1..($cand.Length-1)] --version *> $null; return $cand } catch { }
    }
    throw "Python não encontrado. Instale Python 3.11+."
}
$PY = Get-Py

# --- VENV ROBUSTO ---
$venvDir = Join-Path $Here ".venv"
$venvPy  = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $venvDir)) {
    & $PY[0] $PY[1..($PY.Length-1)] -m venv $venvDir
}

try {
    & $venvPy -c "print('venv-ok')" *> $null
} catch {
    Write-Host "Venv inválido. Recriando..."
    if (Test-Path $venvDir) { Remove-Item -Recurse -Force $venvDir }
    & $PY[0] $PY[1..($PY.Length-1)] -m venv $venvDir
    $venvPy  = Join-Path $venvDir "Scripts\python.exe"
}
# --- FIM VENV ---

# pip e deps
& $venvPy -m pip install -U pip
if (Test-Path "requirements.txt") {
    & $venvPy -m pip install -r requirements.txt
} else {
    & $venvPy -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-WTF python-dotenv bcrypt==4.0.1 "passlib[bcrypt]==1.7.4"
}

# instance e DB
if (-not (Test-Path "instance")) { New-Item -ItemType Directory -Path "instance" | Out-Null }
if (-not (Test-Path "instance\tiger_bank.db")) {
    $env:FLASK_APP = "wsgi:app"
    $code = @"
from tigerbank.extensions import db
from tigerbank import models
from wsgi import app
with app.app_context():
    db.create_all()
    print('DB pronto')
"@
    & $venvPy -c $code
}

# run via python -m
$env:FLASK_APP = "wsgi:app"
& $venvPy -m flask run
