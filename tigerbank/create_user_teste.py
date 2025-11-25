from tigerbank import create_app
from tigerbank.extensions import db
from tigerbank.models import User
from tigerbank.security import hash_password

app = create_app()

email = "teste@tigerbank.com"
senha = "Testando1@"

with app.app_context():
    # Verifica se já existe
    existente = User.query.filter_by(email=email).first()
    if existente:
        print("Usuário já existia no banco remoto.")
        print("ID:", existente.id)
    else:
        novo = User(
            name="Usuário Teste",
            email=email,
            password_hash=hash_password(senha)
        )
        db.session.add(novo)
        db.session.commit()
        print("Usuário criado com sucesso!")
        print("ID:", novo.id)
