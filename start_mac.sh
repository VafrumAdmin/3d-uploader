#!/bin/bash
# ============================================
#  3D Model Multi-Uploader - Start (macOS)
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Aktiviere venv falls vorhanden
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "========================================"
echo "  3D Model Multi-Uploader"
echo "  MakerWorld / Creality Cloud / Makeronline"
echo "========================================"
echo ""

# Backend starten
echo "[1/2] Starte Backend (Port 8100)..."
cd backend
python -m uvicorn main:app --reload --port 8100 &
BACKEND_PID=$!
cd ..

# Frontend starten
echo "[2/2] Starte Frontend (Port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 3
echo ""
echo "App laeuft!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8100"
echo ""

# Browser oeffnen
open http://localhost:5173

echo "Druecke Ctrl+C zum Beenden..."

# Cleanup bei Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
