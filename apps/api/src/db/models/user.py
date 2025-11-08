from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.db.mixins.mixins import IdMixin, TimestampsMixin


class User(Base, IdMixin, TimestampsMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        "email", String(64), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        "username", String(32), unique=True, nullable=False
    )

    passwordHash: Mapped[str] = mapped_column("password_hash", String(64))
