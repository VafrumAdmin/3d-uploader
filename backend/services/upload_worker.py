import asyncio
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import async_session
from models.model3d import Model3D
from models.upload import Upload
from uploaders import get_uploader
from browser.manager import browser_manager

logger = logging.getLogger(__name__)


class UploadWorker:
    def __init__(self):
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._events: asyncio.Queue[dict] = asyncio.Queue(maxsize=100)
        self._running = False

    async def enqueue(self, upload_id: str):
        await self._queue.put(upload_id)

    async def get_event(self) -> dict | None:
        try:
            return self._events.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def _emit(self, event_type: str, data: dict):
        try:
            self._events.put_nowait({"type": event_type, "data": json.dumps(data)})
        except asyncio.QueueFull:
            pass

    async def start(self):
        if self._running:
            return
        self._running = True
        asyncio.create_task(self._worker_loop())
        logger.info("Upload-Worker gestartet")

    async def _worker_loop(self):
        while self._running:
            try:
                upload_id = await asyncio.wait_for(self._queue.get(), timeout=2.0)
                await self._process_upload(upload_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker-Fehler: {e}")

    async def _process_upload(self, upload_id: str):
        async with async_session() as db:
            result = await db.execute(
                select(Upload).where(Upload.id == upload_id)
            )
            upload = result.scalar_one_or_none()
            if not upload or upload.status != "pending":
                return

            # Lade Modell mit Dateien und Bildern
            model_result = await db.execute(
                select(Model3D)
                .where(Model3D.id == upload.model_id)
                .options(selectinload(Model3D.files), selectinload(Model3D.images))
            )
            model = model_result.scalar_one_or_none()
            if not model:
                return

            # Status: running
            upload.status = "running"
            upload.started_at = datetime.now(timezone.utc)
            await db.commit()
            await self._emit("upload_started", {"upload_id": upload_id, "platform": upload.platform, "model_name": model.name})

            try:
                uploader = get_uploader(upload.platform)
                context = await browser_manager.get_upload_context(upload.platform)

                async def on_progress(step: str, percent: int):
                    await self._emit("upload_progress", {
                        "upload_id": upload_id,
                        "step": step,
                        "percent": percent,
                    })

                result_url = await uploader.upload_model(context, model, on_progress)

                upload.status = "success"
                upload.platform_url = result_url
                upload.completed_at = datetime.now(timezone.utc)
                await db.commit()
                await self._emit("upload_completed", {"upload_id": upload_id, "platform": upload.platform, "url": result_url})

                await context.close()
            except Exception as e:
                logger.error(f"Upload fehlgeschlagen für {upload.platform}: {e}")
                upload.status = "failed"
                upload.error_message = str(e)
                upload.completed_at = datetime.now(timezone.utc)
                await db.commit()
                await self._emit("upload_failed", {"upload_id": upload_id, "platform": upload.platform, "error": str(e)})

    async def stop(self):
        self._running = False


upload_worker = UploadWorker()
