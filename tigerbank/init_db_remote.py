from tigerbank import create_app
from tigerbank.extensions import db
from tigerbank.models import User
from tigerbank.security import hash_password

app = create_app()

with app.app_context():
    print("Criando tabelas no banco remoto...")
    db.create_all()
    print("Tabelas criadas com sucesso!")

    email = "teste@tigerbank.com"
    senha = "Testando1@"

    existente = User.query.filter_by(email=email).first()
    if existente:
        print("Usuário já existe:", existente.email)
    else:
        novo = User(
            name="Usuário Teste",
            email=email,
            password_hash=hash_password(senha),
        )
        db.session.add(novo)
        db.session.commit()
        print("Usuário criado com sucesso no banco remoto:", novo.email)
