#!/bin/bash

echo "==== TigerBank Setup (Linux/macOS) ===="

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

if [ ! -f .env ]; then
cat <<EOF > .env
FLASK_ENV=development
FLASK_APP=wsgi.py
DB_HOST=localhost
DB_USER=root
DB_PASS=sua-senha
DB_NAME=tigerbank
EOF
fi

echo "Setup concluído! Execute: flask run"
