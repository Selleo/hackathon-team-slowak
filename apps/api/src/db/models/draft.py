from sqlalchemy import ForeignKey, UUID, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.db.mixins.mixins import IdMixin, TimestampsMixin


class Draft(Base, IdMixin, TimestampsMixin):
    __tablename__ = "drafts"

    draftName: Mapped[str] = mapped_column("draft_name", String, nullable=False)
    userId: Mapped[UUID] = mapped_column("user_id", ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    # threadId: Mapped[str] = mapped_column()
