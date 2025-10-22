@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
  py -3 -m venv .venv || python -m venv .venv
)
call ".venv\Scripts\activate.bat"

python -m pip install -U pip
if exist requirements.txt (
  python -m pip install -r requirements.txt
) else (
  python -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-WTF python-dotenv bcrypt==4.0.1 "passlib[bcrypt]==1.7.4"
)

if not exist instance mkdir instance

if not exist instance\tiger_bank.db (
  set FLASK_APP=wsgi:app
  python - <<PYCODE
from tigerbank.extensions import db
from tigerbank import models
from wsgi import app
with app.app_context():
    db.create_all()
    print("DB pronto")
PYCODE
)

set FLASK_APP=wsgi:app
rem Evita o "launcher" antigo: sempre via "python -m"
python -m flask run
endlocal
