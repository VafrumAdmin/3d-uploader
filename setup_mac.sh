#!/bin/bash
# ============================================
#  3D Model Multi-Uploader - macOS Setup
#  Fuer Apple Silicon (M1/M2/M3/M4)
# ============================================

set -e

echo "========================================"
echo "  3D Model Multi-Uploader - Mac Setup"
echo "========================================"
echo ""

# Pruefen ob Homebrew installiert ist
if ! command -v brew &> /dev/null; then
    echo "Homebrew wird benoetigt. Installiere..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Python 3.12+ pruefen
if ! command -v python3 &> /dev/null; then
    echo "Python3 wird installiert..."
    brew install python@3.12
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python Version: $PYTHON_VERSION"

# Node.js pruefen
if ! command -v node &> /dev/null; then
    echo "Node.js wird installiert..."
    brew install node
fi

NODE_VERSION=$(node --version)
echo "Node.js Version: $NODE_VERSION"

echo ""
echo "[1/5] Erstelle Python Virtual Environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/5] Installiere Python-Abhaengigkeiten..."
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install pyinstaller

echo "[3/5] Installiere Playwright Browser..."
python -m playwright install chromium

echo "[4/5] Installiere Frontend-Abhaengigkeiten..."
cd frontend
npm install
cd ..

echo "[5/5] Baue Frontend..."
cd frontend
npm run build
cd ..

# Kopiere Frontend-Build
rm -rf frontend_dist
cp -r frontend/dist frontend_dist

echo ""
echo "========================================"
echo "  Setup abgeschlossen!"
echo "========================================"
echo ""
echo "Zum Starten (Entwicklungsmodus):"
echo "  ./start_mac.sh"
echo ""
echo "Zum Bauen als macOS App:"
echo "  ./build_mac.sh"
echo ""
