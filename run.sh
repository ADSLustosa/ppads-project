#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Escolhe Python 3
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else echo "Python 3 não encontrado"; exit 1; fi

# venv
if [ ! -d .venv ]; then
    "$PY" -m venv .venv
fi
. .venv/bin/activate

python -m pip install -U pip
if [ -f requirements.txt ]; then
    python -m pip install -r requirements.txt
else
    python -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-WTF python-dotenv bcrypt==4.0.1 "passlib[bcrypt]==1.7.4"
fi

mkdir -p instance

if [ ! -f instance/tiger_bank.db ]; then
    export FLASK_APP="wsgi:app"
    python - <<'PYCODE'
from tigerbank.extensions import db
from tigerbank import models
from wsgi import app
with app.app_context():
    db.create_all()
    print("DB pronto")
PYCODE
fi

export FLASK_APP="wsgi:app"
python -m flask run
