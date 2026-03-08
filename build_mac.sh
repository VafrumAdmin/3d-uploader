#!/bin/bash
# ============================================
#  3D Model Multi-Uploader - macOS App bauen
#  Erzeugt eine signierte .app fuer Apple Silicon
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="3D-Uploader"
BUNDLE_ID="com.3duploader.app"
CERT_NAME="3D-Uploader-Dev"

echo "========================================"
echo "  3D Model Multi-Uploader - App Build"
echo "  Zielplattform: macOS Apple Silicon"
echo "========================================"
echo ""

# Aktiviere venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "FEHLER: .venv nicht gefunden. Fuehre zuerst ./setup_mac.sh aus."
    exit 1
fi

# Pruefen ob PyInstaller installiert ist
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller wird installiert..."
    pip install pyinstaller
fi

# ============================================
#  Schritt 1: Frontend bauen
# ============================================
if [ ! -d "frontend_dist" ]; then
    echo "[1/5] Baue Frontend..."
    cd frontend
    npm run build
    cd ..
    cp -r frontend/dist frontend_dist
else
    echo "[1/5] Frontend-Build vorhanden, ueberspringe..."
fi

# ============================================
#  Schritt 2: Self-Signed Certificate erstellen
# ============================================
echo "[2/5] Erstelle Self-Signed Certificate..."

# Pruefen ob Certificate schon existiert
if security find-identity -v -p codesigning | grep -q "$CERT_NAME"; then
    echo "  Certificate '$CERT_NAME' existiert bereits."
else
    echo "  Erstelle neues Self-Signed Certificate..."

    # Erstelle Certificate-Konfiguration
    cat > /tmp/3d-uploader-cert.plist << 'CERTEOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<array>
    <dict>
        <key>trustRoot</key>
        <true/>
        <key>hashAlgorithm</key>
        <string>sha256</string>
        <key>createPair</key>
        <true/>
        <key>useKeychain</key>
        <string>/Library/Keychains/System.keychain</string>
    </dict>
</array>
</plist>
CERTEOF

    # Erstelle Self-Signed Certificate ueber security-Tool
    # Dies erstellt ein "Code Signing"-faehiges Certificate
    cat > /tmp/create_cert.sh << 'SHEOF'
#!/bin/bash
# Erstelle Self-Signed Certificate fuer Code Signing
CERT_NAME="$1"

# Methode 1: security create-ca (erfordert Keychain-Zugriff)
# Methode 2: openssl + import (zuverlaessiger)

# Generiere Private Key
openssl genrsa -out /tmp/3d-uploader.key 2048

# Generiere Self-Signed Certificate
openssl req -new -x509 \
    -key /tmp/3d-uploader.key \
    -out /tmp/3d-uploader.crt \
    -days 3650 \
    -subj "/CN=$CERT_NAME/O=3D-Uploader Dev" \
    -addext "keyUsage=critical,digitalSignature" \
    -addext "extendedKeyUsage=codeSigning"

# Erstelle .p12 Bundle
openssl pkcs12 -export \
    -out /tmp/3d-uploader.p12 \
    -inkey /tmp/3d-uploader.key \
    -in /tmp/3d-uploader.crt \
    -passout pass:""

# Importiere in Login-Keychain
security import /tmp/3d-uploader.p12 \
    -k ~/Library/Keychains/login.keychain-db \
    -P "" \
    -T /usr/bin/codesign \
    -T /usr/bin/security

# Setze Trust auf "Always Trust" fuer Code Signing
security add-trusted-cert -d -r trustRoot \
    -k ~/Library/Keychains/login.keychain-db \
    /tmp/3d-uploader.crt

# Aufraeumen
rm -f /tmp/3d-uploader.key /tmp/3d-uploader.crt /tmp/3d-uploader.p12

echo "Certificate '$CERT_NAME' erfolgreich erstellt und importiert."
SHEOF
    chmod +x /tmp/create_cert.sh
    /tmp/create_cert.sh "$CERT_NAME"
    rm -f /tmp/create_cert.sh /tmp/3d-uploader-cert.plist
fi

# ============================================
#  Schritt 3: App-Launcher erstellen
# ============================================
echo "[3/5] Erstelle App-Launcher..."
cat > _launcher.py << 'PYEOF'
"""macOS App Launcher fuer 3D Model Multi-Uploader"""
import sys
import os
import webbrowser
import threading
import time
import logging
import logging.handlers

# PyInstaller Bundle-Pfad
if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(bundle_dir)

def open_browser():
    """Oeffne Browser nach kurzem Delay"""
    time.sleep(2)
    webbrowser.open("http://localhost:8100")

if __name__ == "__main__":
    # Browser im Hintergrund oeffnen
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8100,
        log_level="info",
    )
PYEOF

# ============================================
#  Schritt 4: PyInstaller Build
# ============================================
echo "[4/5] Baue macOS App mit PyInstaller..."
pyinstaller \
    --name "$APP_NAME" \
    --windowed \
    --noconfirm \
    --clean \
    --target-arch arm64 \
    --add-data "frontend_dist:frontend_dist" \
    --add-data "backend/config.py:." \
    --add-data "backend/database.py:." \
    --add-data "backend/main.py:." \
    --add-data "backend/models:models" \
    --add-data "backend/schemas:schemas" \
    --add-data "backend/routers:routers" \
    --add-data "backend/services:services" \
    --add-data "backend/browser:browser" \
    --add-data "backend/uploaders:uploaders" \
    --hidden-import uvicorn \
    --hidden-import uvicorn.logging \
    --hidden-import uvicorn.loops \
    --hidden-import uvicorn.loops.auto \
    --hidden-import uvicorn.protocols \
    --hidden-import uvicorn.protocols.http \
    --hidden-import uvicorn.protocols.http.auto \
    --hidden-import uvicorn.protocols.websockets \
    --hidden-import uvicorn.protocols.websockets.auto \
    --hidden-import uvicorn.lifespan \
    --hidden-import uvicorn.lifespan.on \
    --hidden-import fastapi \
    --hidden-import sqlalchemy \
    --hidden-import sqlalchemy.dialects.sqlite \
    --hidden-import aiosqlite \
    --hidden-import multipart \
    --hidden-import sse_starlette \
    --hidden-import config \
    --hidden-import database \
    --hidden-import models \
    --hidden-import models.model3d \
    --hidden-import models.upload \
    --hidden-import models.platform_session \
    --hidden-import schemas \
    --hidden-import schemas.model3d \
    --hidden-import schemas.upload \
    --hidden-import schemas.platform \
    --hidden-import routers \
    --hidden-import routers.models \
    --hidden-import routers.files \
    --hidden-import routers.uploads \
    --hidden-import routers.platforms \
    --hidden-import services \
    --hidden-import services.upload_worker \
    --hidden-import browser \
    --hidden-import browser.manager \
    --hidden-import uploaders \
    --hidden-import uploaders.base_uploader \
    --hidden-import uploaders.makerworld \
    --hidden-import uploaders.crealitycloud \
    --hidden-import uploaders.makeronline \
    --osx-bundle-identifier "$BUNDLE_ID" \
    _launcher.py

# Aufraeuemen
rm -f _launcher.py

# ============================================
#  Schritt 5: Code Signing + Gatekeeper
# ============================================
APP_PATH="dist/$APP_NAME.app"

echo "[5/5] Signiere App..."

if [ -d "$APP_PATH" ]; then
    # Finde das Certificate
    SIGN_IDENTITY=""
    if security find-identity -v -p codesigning | grep -q "$CERT_NAME"; then
        SIGN_IDENTITY="$CERT_NAME"
    fi

    if [ -n "$SIGN_IDENTITY" ]; then
        echo "  Signiere mit Certificate: $SIGN_IDENTITY"

        # Signiere alle Frameworks/Libraries rekursiv
        find "$APP_PATH" -name "*.dylib" -o -name "*.so" | while read lib; do
            codesign --force --sign "$SIGN_IDENTITY" \
                --options runtime \
                --timestamp \
                "$lib" 2>/dev/null || true
        done

        # Signiere die Haupt-Executable
        codesign --force --deep --sign "$SIGN_IDENTITY" \
            --options runtime \
            --timestamp \
            --entitlements /dev/stdin \
            "$APP_PATH" << 'ENTEOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
ENTEOF

        echo "  Verifiziere Signatur..."
        codesign --verify --verbose "$APP_PATH"
        echo "  Signatur OK!"
    else
        echo "  WARNUNG: Kein Signing-Certificate gefunden."
        echo "  App wird ad-hoc signiert (funktioniert lokal)..."

        # Ad-hoc Signing (funktioniert ohne Certificate, aber nur lokal)
        codesign --force --deep --sign - \
            --options runtime \
            "$APP_PATH"
        echo "  Ad-hoc Signatur erstellt."
    fi

    # Quarantine-Attribut entfernen (verhindert "beschaedigte Datei" Meldung)
    xattr -cr "$APP_PATH" 2>/dev/null || true

    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)

    echo ""
    echo "========================================"
    echo "  Build erfolgreich!"
    echo "========================================"
    echo ""
    echo "  App:    $APP_PATH ($APP_SIZE)"
    echo "  Signed: $(codesign -dvv "$APP_PATH" 2>&1 | grep 'Authority' | head -1 || echo 'ad-hoc')"
    echo ""
    echo "  Installation:"
    echo "    cp -r $APP_PATH /Applications/"
    echo ""
    echo "  Direkt starten:"
    echo "    open $APP_PATH"
    echo ""
    echo "  Falls 'beschaedigte Datei' Meldung erscheint:"
    echo "    xattr -cr /Applications/$APP_NAME.app"
    echo "    oder:"
    echo "    sudo spctl --master-disable  (Gatekeeper temporaer aus)"
    echo "    sudo spctl --master-enable   (Gatekeeper wieder an)"
    echo ""
    echo "  WICHTIG: Beim ersten Start Playwright installieren:"
    echo "    python3 -m playwright install chromium"
    echo ""
else
    echo "FEHLER: .app nicht gefunden unter $APP_PATH"
    echo "Pruefe die PyInstaller-Ausgabe oben."
    exit 1
fi
