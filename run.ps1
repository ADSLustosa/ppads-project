# run.ps1 - setup + run usando Python do VSCode/Path
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

function Get-Py {
    $cands = @(
        @("python"),
        @("py","-3.12"),
        @("py","-3.11"),
        @("py","-3")
    )
    foreach ($cand in $cands) {
        try {
            & $cand[0] $cand[1..($cand.Length-1)] --version *> $null
            return $cand
        } catch { }
    }
    throw "Python não encontrado. Instale Python 3.11+."
}
$PY = Get-Py

# venv local
if (-not (Test-Path ".venv")) {
    & $PY[0] $PY[1..($PY.Length-1)] -m venv .venv
}
$venvPy = Join-Path $Here ".venv\Scripts\python.exe"

# pip atualizado
& $venvPy -m pip install -U pip

# dependências
if (Test-Path "requirements.txt") {
    & $venvPy -m pip install -r requirements.txt
} else {
    & $venvPy -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-WTF python-dotenv bcrypt==4.0.1 "passlib[bcrypt]==1.7.4"
}

# instance/
if (-not (Test-Path "instance")) { New-Item -ItemType Directory -Path "instance" | Out-Null }

# DB se ausente
if (-not (Test-Path "instance\tiger_bank.db")) {
    $env:FLASK_APP = "wsgi:app"
    $code = @'
from tigerbank.extensions import db
from tigerbank import models
from wsgi import app
with app.app_context():
    db.create_all()
    print("DB pronto")
'@
    & $venvPy -c $code
}

# Executar Flask sempre via "python -m"
$env:FLASK_APP = "wsgi:app"
& $venvPy -m flask run
