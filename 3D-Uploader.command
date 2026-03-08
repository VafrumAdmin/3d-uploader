#!/bin/bash
# ============================================
#  3D Model Multi-Uploader
#  Doppelklick zum Starten auf macOS
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Einmalige Ersteinrichtung
if [ ! -d ".venv" ]; then
    echo "Ersteinrichtung laeuft..."
    echo ""

    # Python venv erstellen
    python3 -m venv .venv
    source .venv/bin/activate

    # Abhaengigkeiten installieren
    pip install --upgrade pip
    pip install -r backend/requirements.txt

    # Playwright Chromium installieren
    python -m playwright install chromium

    # Frontend bauen
    if [ ! -d "frontend_dist" ]; then
        cd frontend
        npm install
        npm run build
        cd ..
        cp -r frontend/dist frontend_dist
    fi

    echo ""
    echo "Ersteinrichtung abgeschlossen!"
    echo ""
fi

# Aktiviere venv
source .venv/bin/activate

# Prüfe ob Frontend-Build existiert
if [ ! -d "frontend_dist" ]; then
    echo "Frontend wird gebaut..."
    cd frontend
    npm install
    npm run build
    cd ..
    cp -r frontend/dist frontend_dist
fi

echo "========================================"
echo "  3D Model Multi-Uploader"
echo "========================================"
echo ""
echo "Starte Server auf http://localhost:8100"
echo ""

# Öffne Browser nach 2 Sekunden
(sleep 2 && open http://localhost:8100) &

# Starte Server (Frontend wird vom Backend ausgeliefert)
cd backend
python -m uvicorn main:app --port 8100
