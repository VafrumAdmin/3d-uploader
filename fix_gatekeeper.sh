#!/bin/bash
# ============================================
#  Gatekeeper-Fix fuer 3D Model Multi-Uploader
#
#  Ausfuehren wenn die App nicht startet wegen:
#  - "App ist beschaedigt und kann nicht geoeffnet werden"
#  - "App kann nicht geoeffnet werden, da sie von einem
#     nicht identifizierten Entwickler stammt"
# ============================================

APP_NAME="3D-Uploader"

echo "========================================"
echo "  Gatekeeper-Fix fuer $APP_NAME"
echo "========================================"
echo ""

# Pruefen wo die App liegt
if [ -d "/Applications/$APP_NAME.app" ]; then
    APP_PATH="/Applications/$APP_NAME.app"
elif [ -d "dist/$APP_NAME.app" ]; then
    APP_PATH="dist/$APP_NAME.app"
else
    echo "FEHLER: $APP_NAME.app nicht gefunden."
    echo "Erwartet in /Applications/ oder dist/"
    exit 1
fi

echo "App gefunden: $APP_PATH"
echo ""

# Methode 1: Quarantine-Attribut entfernen (meistens ausreichend)
echo "[1/3] Entferne Quarantine-Attribut..."
xattr -cr "$APP_PATH"
echo "  Erledigt."

# Methode 2: App ad-hoc signieren
echo "[2/3] Ad-hoc Code Signing..."
codesign --force --deep --sign - "$APP_PATH" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  Erledigt."
else
    echo "  Uebersprungen (nicht kritisch)."
fi

# Methode 3: Gatekeeper-Ausnahme hinzufuegen
echo "[3/3] Fuge Gatekeeper-Ausnahme hinzu..."
spctl --add --label "$APP_NAME" "$APP_PATH" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  Erledigt."
else
    echo "  Benoeigt sudo-Rechte. Versuche mit sudo..."
    sudo spctl --add --label "$APP_NAME" "$APP_PATH" 2>/dev/null || true
fi

echo ""
echo "========================================"
echo "  Fix angewendet!"
echo "========================================"
echo ""
echo "Versuche jetzt die App zu starten:"
echo "  open \"$APP_PATH\""
echo ""
echo "Falls es immer noch nicht funktioniert:"
echo ""
echo "  Option A: Rechtsklick auf die App -> 'Oeffnen'"
echo "            (beim ersten Mal erscheint ein Dialog"
echo "             mit 'Oeffnen'-Button)"
echo ""
echo "  Option B: Systemeinstellungen -> Datenschutz &"
echo "            Sicherheit -> Runterscrollen ->"
echo "            '$APP_NAME wurde blockiert' ->"
echo "            'Trotzdem oeffnen'"
echo ""
echo "  Option C (letzter Ausweg):"
echo "    sudo spctl --master-disable"
echo "    open \"$APP_PATH\""
echo "    sudo spctl --master-enable"
echo ""
