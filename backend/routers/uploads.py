import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from config import PLATFORMS
from database import get_db
from models.model3d import Model3D
from models.upload import Upload
from schemas.model3d import UploadOut
from schemas.upload import UploadRequest
from services.upload_worker import upload_worker

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.get("", response_model=list[UploadOut])
async def list_uploads(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).order_by(Upload.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=list[UploadOut], status_code=201)
async def create_uploads(data: UploadRequest, db: AsyncSession = Depends(get_db)):
    # Prüfe ob Modell existiert
    result = await db.execute(
        select(Model3D)
        .where(Model3D.id == data.model_id)
        .options(selectinload(Model3D.files), selectinload(Model3D.images))
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Modell nicht gefunden")

    if not model.files:
        raise HTTPException(400, "Modell hat keine 3D-Dateien")

    created = []
    for platform in data.platforms:
        if platform not in PLATFORMS:
            continue

        # Prüfe auf Doppel-Upload
        existing = await db.execute(
            select(Upload).where(Upload.model_id == data.model_id, Upload.platform == platform)
        )
        existing_upload = existing.scalar_one_or_none()

        if existing_upload:
            if existing_upload.status == "success":
                continue  # Bereits erfolgreich hochgeladen
            # Fehlgeschlagenen Upload neu versuchen
            existing_upload.status = "pending"
            existing_upload.error_message = None
            existing_upload.started_at = None
            existing_upload.completed_at = None
            created.append(existing_upload)
        else:
            upload = Upload(model_id=data.model_id, platform=platform, status="pending")
            db.add(upload)
            created.append(upload)

    await db.commit()
    for u in created:
        await db.refresh(u)

    # Zur Queue hinzufügen
    for u in created:
        await upload_worker.enqueue(u.id)

    return created


@router.post("/{upload_id}/retry", response_model=UploadOut)
async def retry_upload(upload_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).where(Upload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(404, "Upload nicht gefunden")

    upload.status = "pending"
    upload.error_message = None
    upload.started_at = None
    upload.completed_at = None
    await db.commit()
    await db.refresh(upload)

    await upload_worker.enqueue(upload.id)
    return upload


@router.post("/{upload_id}/cancel", response_model=UploadOut)
async def cancel_upload(upload_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).where(Upload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(404, "Upload nicht gefunden")
    if upload.status not in ("pending", "running"):
        raise HTTPException(400, "Upload kann nicht abgebrochen werden")

    upload.status = "cancelled"
    upload.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(upload)
    return upload


@router.get("/stream")
async def upload_stream():
    async def event_generator():
        while True:
            event = await upload_worker.get_event()
            if event:
                yield {"event": event["type"], "data": event["data"]}
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())
