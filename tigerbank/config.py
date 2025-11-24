from __future__ import annotations
import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

def _normalize_database_url(url: str) -> str:
    """
    Normaliza URLs vindas do Render para psycopg3 com SSL obrigatório.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)

    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Garante SSL mesmo se não estiver na URL original
    if "sslmode=" not in url:
        if "?" in url:
            url += "&sslmode=require"
        else:
            url += "?sslmode=require"

    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe-change-me")

    raw = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'tiger_bank.db').as_posix()}",
    )

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(raw)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    DEBUG = os.getenv("FLASK_ENV") == "development"
    TEMPLATES_AUTO_RELOAD = DEBUG
    SEND_FILE_MAX_AGE_DEFAULT = 0 if DEBUG else None


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
