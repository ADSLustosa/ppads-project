@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat

pip install -U pip
pip install -r requirements.txt
pip install bcrypt==4.0.1 passlib[bcrypt]==1.7.4

if not exist instance mkdir instance
if not exist instance\tiger_bank.db (
  set FLASK_APP=app.py
  python -c "from tigerbank.extensions import db; from tigerbank import models; from app import app; 
from contextlib import suppress; 
with app.app_context(): db.create_all(); print('DB pronto')"
)

set FLASK_APP=app.py
set FLASK_ENV=development
flask run
endlocal
