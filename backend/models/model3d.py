import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Model3D(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    license: Mapped[str] = mapped_column(String(50), default="CC-BY-4.0")
    is_remix: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    files: Mapped[list["ModelFile"]] = relationship(back_populates="model", cascade="all, delete-orphan")
    images: Mapped[list["ModelImage"]] = relationship(back_populates="model", cascade="all, delete-orphan")
    uploads: Mapped[list["Upload"]] = relationship(back_populates="model", cascade="all, delete-orphan")


class ModelFile(Base):
    __tablename__ = "model_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id: Mapped[str] = mapped_column(String(36), ForeignKey("models.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    filepath: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(10))
    file_size: Mapped[int] = mapped_column(Integer)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    model: Mapped["Model3D"] = relationship(back_populates="files")


class ModelImage(Base):
    __tablename__ = "model_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id: Mapped[str] = mapped_column(String(36), ForeignKey("models.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    filepath: Mapped[str] = mapped_column(String(500))
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    model: Mapped["Model3D"] = relationship(back_populates="images")
