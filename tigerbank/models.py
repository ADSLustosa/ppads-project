from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tigerbank.extensions import db, login_manager


# -------------------------- ENUM --------------------------
class AccountType(str, Enum):
    CORRENTE = "Corrente"
    POUPANCA = "Poupança"


# ------------------------- USER --------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    cpf: Mapped[str] = mapped_column(db.String(11), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    
    def set_password(self, password: str) -> None:
        
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return str(self.id)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id: str) -> Optional["User"]:
    """Necessário para o Flask-Login."""
    return User.query.get(int(user_id))


# -------------------------- ACCOUNT --------------------------
class Account(db.Model):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    type: Mapped[str] = mapped_column(
        db.String(20), default=AccountType.CORRENTE.value, nullable=False
    )
    balance: Mapped[float] = mapped_column(db.Numeric(14, 2), default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="account")
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    loans: Mapped[List["Loan"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    investments: Mapped[List["Investment"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Account {self.id} - {self.user.name}>"


# -------------------------- TRANSACTION -------------------------
class Transaction(db.Model):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(
        db.String(40), nullable=False
    )  
    amount: Mapped[float] = mapped_column(db.Numeric(14, 2), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), default="")
    balance_after: Mapped[float] = mapped_column(db.Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="transactions")


# -------------------------- LOAN --------------------------
class Loan(db.Model):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    principal: Mapped[float] = mapped_column(db.Numeric(14, 2), nullable=False)
    months: Mapped[int] = mapped_column(db.Integer, nullable=False)
    monthly_rate: Mapped[float] = mapped_column(db.Float, default=0.025, nullable=False)
    installment_amount: Mapped[float] = mapped_column(db.Numeric(14, 2), nullable=False)
    remaining_installments: Mapped[int] = mapped_column(db.Integer, nullable=False)
    hired_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="loans")


# -------------------------- INVESTMENT --------------------------
class Investment(db.Model):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    product: Mapped[str] = mapped_column(
        db.String(40), nullable=False
    )  # Poupança, CDB, Ações
    monthly_rate: Mapped[float] = mapped_column(db.Float, nullable=False)
    principal: Mapped[float] = mapped_column(db.Numeric(14, 2), nullable=False)
    months: Mapped[int] = mapped_column(db.Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="investments")
