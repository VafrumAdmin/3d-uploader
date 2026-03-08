import logging
import logging.handlers
import sys
import traceback
import webbrowser
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import STORAGE_DIR, LOGS_DIR
from database import init_db
from routers import models, files, uploads, platforms
from services.upload_worker import upload_worker
from browser.manager import browser_manager

# ============================================
#  Logging-System
# ============================================

LOG_FILE = LOGS_DIR / "3d-uploader.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"

# Formatter mit Zeitstempel, Level, Modul, Nachricht
log_format = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Root-Logger konfigurieren
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Console-Handler (INFO+)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
root_logger.addHandler(console_handler)

# Datei-Handler: Alles (DEBUG+)
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
root_logger.addHandler(file_handler)

# Error-Log: Nur Fehler (ERROR+)
error_handler = logging.handlers.RotatingFileHandler(
    ERROR_LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(log_format)
root_logger.addHandler(error_handler)

logger = logging.getLogger("main")

# ============================================
#  App-Pfade
# ============================================

if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BUNDLE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BUNDLE_DIR / "frontend_dist"


# ============================================
#  App Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("3D Model Multi-Uploader startet...")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
    logger.info(f"Storage: {STORAGE_DIR}")
    logger.info(f"Logs: {LOGS_DIR}")
    logger.info(f"Frontend: {FRONTEND_DIR} (exists: {FRONTEND_DIR.exists()})")
    logger.info("=" * 60)

    await init_db()
    await upload_worker.start()
    logger.info("Backend gestartet und bereit")

    if getattr(sys, "frozen", False):
        webbrowser.open("http://localhost:8100")

    yield
    await upload_worker.stop()
    await browser_manager.close()
    logger.info("Backend heruntergefahren")


app = FastAPI(title="3D Model Multi-Uploader", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
#  Globaler Exception-Handler
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Unbehandelte Exception auf {request.method} {request.url.path}:\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ============================================
#  Request-Logging Middleware
# ============================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now(timezone.utc)
    try:
        response = await call_next(request)
        duration = (datetime.now(timezone.utc) - start).total_seconds()

        # Nur API-Requests loggen (nicht statische Dateien)
        if request.url.path.startswith("/api"):
            logger.debug(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)"
            )

        return response
    except Exception as e:
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        logger.error(
            f"{request.method} {request.url.path} -> FEHLER nach {duration:.3f}s: {e}"
        )
        raise


# Statische Dateien (Bilder, 3D-Dateien aus der DB)
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

# Router
app.include_router(models.router)
app.include_router(files.router)
app.include_router(uploads.router)
app.include_router(platforms.router)


# ============================================
#  Debug / Log API-Endpunkte
# ============================================

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "python": sys.version,
        "frozen": getattr(sys, "frozen", False),
        "storage": str(STORAGE_DIR),
        "log_file": str(LOG_FILE),
    }


@app.get("/api/logs")
async def get_logs(lines: int = 100, level: str = "all"):
    """Letzte Log-Zeilen lesen (fuer Debug-Panel im UI)"""
    log_path = ERROR_LOG_FILE if level == "error" else LOG_FILE
    if not log_path.exists():
        return {"lines": [], "file": str(log_path)}

    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()

    return {
        "lines": [line.rstrip() for line in all_lines[-lines:]],
        "file": str(log_path),
        "total_lines": len(all_lines),
    }


@app.get("/api/logs/download")
async def download_logs():
    """Komplettes Log als Datei herunterladen"""
    if LOG_FILE.exists():
        return FileResponse(
            LOG_FILE,
            filename=f"3d-uploader-log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log",
            media_type="text/plain",
        )
    return JSONResponse({"detail": "Keine Log-Datei vorhanden"}, status_code=404)


@app.get("/api/logs/errors/download")
async def download_error_logs():
    """Error-Log als Datei herunterladen"""
    if ERROR_LOG_FILE.exists():
        return FileResponse(
            ERROR_LOG_FILE,
            filename=f"3d-uploader-errors-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log",
            media_type="text/plain",
        )
    return JSONResponse({"detail": "Keine Error-Log-Datei vorhanden"}, status_code=404)


# ============================================
#  Frontend (SPA-Fallback)
# ============================================

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="frontend_assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
