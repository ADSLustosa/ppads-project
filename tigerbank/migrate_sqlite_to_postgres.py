import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tigerbank import create_app
from tigerbank.extensions import db
from tigerbank.models import User, Account, Transaction  # ajuste se tiver mais modelos

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

SQLITE_PATH = "instance/tiger_bank.db"

POSTGRES_URL = os.getenv("DATABASE_URL")
if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql+psycopg://", 1)

app = create_app()

# ==========================================================
# CONEXÃO SQLITE (ORIGEM)
# ==========================================================
sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

# ==========================================================
# CONEXÃO POSTGRES (DESTINO)
# ==========================================================
pg_engine = create_engine(POSTGRES_URL)
PGSession = sessionmaker(bind=pg_engine)
pg_session = PGSession()

# ==========================================================
# CRIAR TABELAS NO POSTGRES
# ==========================================================
with app.app_context():
    db.create_all()


# ==========================================================
# FUNÇÃO GENÉRICA DE MIGRAÇÃO
# ==========================================================
def migrate_table(Model):
    table_name = Model.__tablename__
    print(f"-> Migrando tabela: {table_name}")

    rows = sqlite_session.query(Model).all()
    if not rows:
        print(f"   Nenhum registro encontrado em {table_name}.")
        return

    for row in rows:
        data = {col: getattr(row, col) for col in row.__table__.columns.keys()}
        obj = Model(**data)
        pg_session.merge(obj)

    pg_session.commit()
    print(f"   OK! Registros migrados: {len(rows)}")


# ==========================================================
# MIGRAR TABELAS NA ORDEM CORRETA
# ==========================================================

# Ajuste conforme seus modelos:
tables_in_order = [User, Account, Transaction]

for table in tables_in_order:
    migrate_table(table)

print("\n✔ MIGRAÇÃO CONCLUÍDA COM SUCESSO!\n")
