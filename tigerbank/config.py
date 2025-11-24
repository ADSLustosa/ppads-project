from __future__ import annotations
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


def _normalize_database_url(url: str) -> str:
    """
    Corrige URLs do Render:
    - 'postgres://' → legado (usa psycopg2)
    - Convertido para 'postgresql+psycopg://' → psycopg3
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)

    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe-change-me")
    WTF_CSRF_ENABLED = False

    # Banco: Render (PostgreSQL) | Local (SQLite)
    raw_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'tiger_bank.db').as_posix()}",
    )

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(raw_url)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Ambiente
    DEBUG = os.getenv("FLASK_ENV") == "development"
    TEMPLATES_AUTO_RELOAD = DEBUG
    SEND_FILE_MAX_AGE_DEFAULT = 0 if DEBUG else None


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
