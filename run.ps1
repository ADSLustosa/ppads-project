Write-Host "==== TigerBank Setup (Windows) ===="

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

if (!(Test-Path ".env")) {
@"
FLASK_ENV=development
FLASK_APP=wsgi.py
DB_HOST=localhost
DB_USER=root
DB_PASS=sua-senha
DB_NAME=tigerbank
"@ | Out-File -Encoding utf8 .env
}

Write-Host "Setup concluído! Execute: flask run"
