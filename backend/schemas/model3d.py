from datetime import datetime
from pydantic import BaseModel


class ModelFileOut(BaseModel):
    id: str
    filename: str
    filepath: str
    file_type: str
    file_size: int
    file_hash: str | None = None

    class Config:
        from_attributes = True


class ModelImageOut(BaseModel):
    id: str
    filename: str
    filepath: str
    is_cover: bool
    sort_order: int

    class Config:
        from_attributes = True


class UploadOut(BaseModel):
    id: str
    platform: str
    status: str
    platform_url: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class ModelCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    tags: str | None = None
    license: str = "CC-BY-4.0"
    is_remix: bool = False


class ModelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    tags: str | None = None
    license: str | None = None
    is_remix: bool | None = None


class ModelOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    category: str | None = None
    tags: str | None = None
    license: str
    is_remix: bool
    created_at: datetime
    updated_at: datetime
    files: list[ModelFileOut] = []
    images: list[ModelImageOut] = []
    uploads: list[UploadOut] = []

    class Config:
        from_attributes = True
