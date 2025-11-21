
# Tiger Bank (Flask)

Arquitetura limpa e camadas.
Banco: SQLite por padrão (`instance/tiger_bank.db`).

## Rodar

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=app.py  # Windows: set FLASK_APP=app.py
flask db upgrade
flask run
```

## Testes
```bash
pytest -q
```

## Notas de segurança
- Hash de senha com bcrypt.
- Valida CPF, e-mail, força de senha.
- Transações atômicas no serviço com `session.begin()`.
- Proteção CSRF via Flask-WTF.
