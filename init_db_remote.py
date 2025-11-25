from tigerbank import create_app
from tigerbank.extensions import db
from tigerbank.models import User
from tigerbank.security import hash_password

app = create_app()

with app.app_context():
    print("Criando tabelas no PostgreSQL remoto...")
    db.create_all()
    print("Tabelas criadas!")

    email = "teste@tigerbank.com"
    senha = "Testando1@"

    user = User.query.filter_by(email=email).first()

    if user:
        print("Usuário já existe:", user.email)
    else:
        novo = User(
            name="Usuário Teste",
            email=email,
            password_hash=hash_password(senha)
        )
        db.session.add(novo)
        db.session.commit()
        print("Usuário criado:", novo.email)
