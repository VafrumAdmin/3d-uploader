import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class PlatformSession(Base):
    __tablename__ = "platform_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_logged_in: Mapped[bool] = mapped_column(Boolean, default=False)
    session_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_verified: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
