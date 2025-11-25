import os
from tigerbank import create_app
from tigerbank.extensions import db
from tigerbank.models import User

# 1. Usa o DATABASE_URL do Render já configurado no .env
app = create_app()

with app.app_context():
    print("Criando tabelas no banco remoto...")
    db.create_all()

    # 2. Cria o usuário de teste
    email = "teste@tigerbank.com"
    senha = "Testando1@"

    existing = User.query.filter_by(email=email).first()
    if not existing:
        user = User(
            name="Usuário Teste",
            email=email,
            cpf="00000000000"
        )
        user.set_password(senha)
        db.session.add(user)
        db.session.commit()
        print("Usuário criado com sucesso!")
    else:
        print("Usuário já existe. Nenhuma alteração feita.")

    print("Banco remoto inicializado com sucesso!")
