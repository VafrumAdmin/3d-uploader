import hashlib
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import MODELS_DIR, IMAGES_DIR
from database import get_db
from models.model3d import Model3D, ModelFile, ModelImage
from schemas.model3d import ModelFileOut, ModelImageOut

router = APIRouter(prefix="/api/models", tags=["files"])

ALLOWED_3D_EXTENSIONS = {".stl", ".3mf", ".obj", ".step", ".stp", ".f3d", ".scad", ".blend", ".zip"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def compute_hash(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@router.post("/{model_id}/files", response_model=list[ModelFileOut])
async def upload_files(
    model_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Model3D).where(Model3D.id == model_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Modell nicht gefunden")

    model_dir = MODELS_DIR / model_id
    model_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_3D_EXTENSIONS:
            continue

        file_id = str(uuid.uuid4())
        dest = model_dir / f"{file_id}{ext}"
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_hash = compute_hash(dest)
        model_file = ModelFile(
            model_id=model_id,
            filename=file.filename,
            filepath=str(dest),
            file_type=ext.lstrip("."),
            file_size=dest.stat().st_size,
            file_hash=file_hash,
        )
        db.add(model_file)
        created.append(model_file)

    await db.commit()
    for f in created:
        await db.refresh(f)
    return created


@router.delete("/{model_id}/files/{file_id}", status_code=204)
async def delete_file(model_id: str, file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelFile).where(ModelFile.id == file_id, ModelFile.model_id == model_id))
    model_file = result.scalar_one_or_none()
    if not model_file:
        raise HTTPException(404, "Datei nicht gefunden")
    filepath = Path(model_file.filepath)
    if filepath.exists():
        filepath.unlink()
    await db.delete(model_file)
    await db.commit()


@router.post("/{model_id}/images", response_model=list[ModelImageOut])
async def upload_images(
    model_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Model3D).where(Model3D.id == model_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Modell nicht gefunden")

    img_dir = IMAGES_DIR / model_id
    img_dir.mkdir(parents=True, exist_ok=True)

    # Zähle existierende Bilder für sort_order
    existing = await db.execute(select(ModelImage).where(ModelImage.model_id == model_id))
    count = len(existing.scalars().all())

    created = []
    for i, file in enumerate(files):
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            continue

        img_id = str(uuid.uuid4())
        dest = img_dir / f"{img_id}{ext}"
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)

        image = ModelImage(
            model_id=model_id,
            filename=file.filename,
            filepath=str(dest),
            is_cover=(count == 0 and i == 0),
            sort_order=count + i,
        )
        db.add(image)
        created.append(image)

    await db.commit()
    for img in created:
        await db.refresh(img)
    return created


@router.delete("/{model_id}/images/{image_id}", status_code=204)
async def delete_image(model_id: str, image_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelImage).where(ModelImage.id == image_id, ModelImage.model_id == model_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(404, "Bild nicht gefunden")
    filepath = Path(image.filepath)
    if filepath.exists():
        filepath.unlink()
    await db.delete(image)
    await db.commit()


@router.get("/{model_id}/files/{file_id}/download")
async def download_file(model_id: str, file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelFile).where(ModelFile.id == file_id, ModelFile.model_id == model_id))
    model_file = result.scalar_one_or_none()
    if not model_file:
        raise HTTPException(404, "Datei nicht gefunden")
    return FileResponse(model_file.filepath, filename=model_file.filename)


@router.get("/{model_id}/images/{image_id}/view")
async def view_image(model_id: str, image_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelImage).where(ModelImage.id == image_id, ModelImage.model_id == model_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(404, "Bild nicht gefunden")
    return FileResponse(image.filepath)
