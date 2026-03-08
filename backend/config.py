import sys
from pathlib import Path

# Im gepackten Modus (PyInstaller) nutze den Home-Ordner für persistente Daten
if getattr(sys, "frozen", False):
    STORAGE_DIR = Path.home() / ".3d-uploader"
else:
    BASE_DIR = Path(__file__).resolve().parent
    STORAGE_DIR = BASE_DIR / "storage"

MODELS_DIR = STORAGE_DIR / "models"
IMAGES_DIR = STORAGE_DIR / "images"
SESSIONS_DIR = STORAGE_DIR / "sessions"
LOGS_DIR = STORAGE_DIR / "logs"
DATABASE_URL = f"sqlite+aiosqlite:///{STORAGE_DIR / '3d_uploader.db'}"

PLATFORMS = {
    "makerworld": {
        "name": "MakerWorld",
        "login_url": "https://makerworld.com/en",
        "upload_url": "https://makerworld.com/en/u/upload",
        "color": "#00AE42",
    },
    "crealitycloud": {
        "name": "Creality Cloud",
        "login_url": "https://www.crealitycloud.com",
        "upload_url": "https://www.crealitycloud.com",
        "color": "#1E88E5",
    },
    "makeronline": {
        "name": "Makeronline",
        "login_url": "https://makeronline.com",
        "upload_url": "https://makeronline.com",
        "color": "#FF6B00",
    },
}

# Storage-Ordner sicherstellen
for d in [MODELS_DIR, IMAGES_DIR, SESSIONS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
