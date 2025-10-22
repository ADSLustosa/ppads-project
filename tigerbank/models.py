
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from flask_login import UserMixin
from sqlalchemy import func, CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .extensions import db, login_manager

class AccountType(str, Enum):
    CORRENTE = "Corrente"
    POUPANCA = "Poupança"

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    cpf: Mapped[str] = mapped_column(db.String(11), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    def get_id(self) -> str:
        return str(self.id)

@login_manager.user_loader
def load_user(user_id: str) -> Optional["User"]:
    return User.query.get(int(user_id))

class Account(db.Model):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(db.String(20), default=AccountType.CORRENTE.value, nullable=False)
    balance: Mapped[float] = mapped_column(db.Numeric(14,2), default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="account")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    loans: Mapped[list["Loan"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    investments: Mapped[list["Investment"]] = relationship(back_populates="account", cascade="all, delete-orphan")

class Transaction(db.Model):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    kind: Mapped[str] = mapped_column(db.String(40), nullable=False)  # Deposito, Saque, Transferencia, PIX, Investimento, Resgate, Emprestimo
    amount: Mapped[float] = mapped_column(db.Numeric(14,2), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), default="")
    balance_after: Mapped[float] = mapped_column(db.Numeric(14,2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="transactions")

class Loan(db.Model):
    __tablename__ = "loans"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    principal: Mapped[float] = mapped_column(db.Numeric(14,2), nullable=False)
    months: Mapped[int] = mapped_column(db.Integer, nullable=False)
    monthly_rate: Mapped[float] = mapped_column(db.Float, default=0.025, nullable=False)
    installment_amount: Mapped[float] = mapped_column(db.Numeric(14,2), nullable=False)
    remaining_installments: Mapped[int] = mapped_column(db.Integer, nullable=False)
    hired_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="loans")

class Investment(db.Model):
    __tablename__ = "investments"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    product: Mapped[str] = mapped_column(db.String(40), nullable=False)  # Poupança, CDB, Acoes
    monthly_rate: Mapped[float] = mapped_column(db.Float, nullable=False)
    principal: Mapped[float] = mapped_column(db.Numeric(14,2), nullable=False)
    months: Mapped[int] = mapped_column(db.Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="investments")
