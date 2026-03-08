# 3D Model Multi-Uploader

Lade deine 3D-Modelle automatisch auf MakerWorld, Creality Cloud und Makeronline hoch –
ohne jedes Modell einzeln auf jeder Plattform manuell hochzuladen.

---

## Installation (Windows)

### Voraussetzungen

- **Python 3.10 oder hoeher**
  - Download: https://www.python.org/downloads/
  - **WICHTIG:** Bei der Installation den Haken bei **"Add Python to PATH"** setzen!
- Internetzugang

### Schritt 1: ZIP entpacken

Entpacke die ZIP-Datei an einen beliebigen Ort, z.B. auf den Desktop.

### Schritt 2: Installation starten

Doppelklicke auf **`install_windows.bat`**

Das Script installiert automatisch:
- Python Virtual Environment mit allen Abhaengigkeiten
- Playwright Chromium Browser (fuer die Upload-Automatisierung)
- Datenverzeichnisse

Dauer: ca. 2-5 Minuten je nach Internetgeschwindigkeit.

### Schritt 3: App starten

Doppelklicke auf **`start_standalone.bat`**

Die App oeffnet sich automatisch im Browser unter **http://localhost:8100**

---

## Installation (macOS Apple Silicon)

### Voraussetzungen

- macOS 12+ auf einem Mac mit M1/M2/M3/M4 Prozessor
- Internetzugang

### Schritt 1: ZIP entpacken

Entpacke die ZIP-Datei an einen beliebigen Ort, z.B. auf den Desktop.

### Schritt 2: Terminal oeffnen

Oeffne das Terminal (Programme > Dienstprogramme > Terminal) und navigiere in den entpackten Ordner:

```bash
cd ~/Desktop/3d-uploader
```

### Schritt 3: Setup ausfuehren

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

Das Script installiert automatisch:
- Python Virtual Environment mit allen Abhaengigkeiten
- Playwright Chromium Browser (fuer die Upload-Automatisierung)
- Node.js Frontend-Abhaengigkeiten
- Baut das Frontend

Dauer: ca. 2-5 Minuten je nach Internetgeschwindigkeit.

### Schritt 4: App starten

**Option A – Einfachster Weg (Doppelklick):**

Doppelklicke auf `3D-Uploader.command` im Finder.
Falls macOS fragt: Rechtsklick > "Oeffnen" > "Oeffnen" bestaetigen.

**Option B – Terminal:**

```bash
./start_mac.sh
```

Die App oeffnet sich automatisch im Browser unter http://localhost:8100

---

## Erste Schritte nach dem Start

### 1. Bei den Plattformen einloggen

Gehe zu **Einstellungen** (in der linken Sidebar).

Dort siehst du drei Plattformen:
- **MakerWorld** (Bambu Lab)
- **Creality Cloud**
- **Makeronline** (Anycubic)

Klicke bei jeder Plattform auf **"Einloggen"**:
1. Ein Chromium-Browser oeffnet sich
2. Logge dich dort ganz normal mit deinen Zugangsdaten ein
3. Schliesse das Browser-Fenster nach dem Login

Die Session wird gespeichert – du musst dich nicht jedes Mal neu einloggen.

**Tipp:** Du brauchst auf jeder Plattform einen Account. Falls du noch keinen hast:
- MakerWorld: https://makerworld.com
- Creality Cloud: https://www.crealitycloud.com
- Makeronline: https://makeronline.com

### 2. Erstes Modell erstellen

Klicke auf **"Neues Modell"** in der Sidebar.

**3D-Dateien hochladen:**
- Ziehe deine STL, 3MF oder OBJ Dateien in das Feld
- Oder klicke auf das Feld um Dateien auszuwaehlen

**Bilder hochladen:**
- Ziehe Cover-Fotos (JPG, PNG) in das Bilder-Feld
- MakerWorld verlangt echte Druckfotos (keine Renders!)
- Das erste Bild wird automatisch als Titelbild gesetzt

**Metadaten ausfuellen:**
- **Modellname** – z.B. "Phone Stand V2" (Pflichtfeld)
- **Beschreibung** – Was das Modell ist, Druckhinweise, etc.
- **Kategorie** – Waehle eine passende Kategorie
- **Tags** – Kommasepariert, z.B. "phone, stand, desk, functional"
- **Lizenz** – Standard ist CC-BY 4.0
- **Remix** – Haken setzen wenn es ein Remix eines anderen Modells ist

### 3. Plattformen auswaehlen und hochladen

Unter dem Formular siehst du drei Plattform-Karten:
- Klicke auf die Plattformen auf die du hochladen willst
- Ausgewaehlte Plattformen werden farbig hervorgehoben

Dann klicke:
- **"Nur Speichern"** – Speichert das Modell lokal, laedt noch nicht hoch
- **"Speichern & Hochladen"** – Speichert und startet sofort den Upload

### 4. Upload verfolgen

Gehe zu **"Upload-Queue"** in der Sidebar:
- Sieh den Status jedes Uploads (Wartend, Laeuft, Erfolgreich, Fehlgeschlagen)
- Bei Fehlern: Klicke auf das Refresh-Symbol um es nochmal zu versuchen
- Bei Erfolg: Klicke auf den Link um dein Modell auf der Plattform anzusehen

### 5. Weitere Modelle hochladen

Auf der **Dashboard**-Seite siehst du alle deine Modelle als Karten.
Jede Karte zeigt:
- Vorschaubild
- Anzahl Dateien und Bilder
- Status pro Plattform (gruen = hochgeladen, grau = nicht, rot = Fehler)

Klicke auf eine Karte um die Details zu sehen und weitere Uploads zu starten.

---

## Features im Detail

### Doppel-Upload-Schutz

Das Tool merkt sich welche Modelle auf welcher Plattform hochgeladen wurden.
Bereits hochgeladene Plattformen werden als "Bereits hochgeladen" markiert
und die Checkbox ist deaktiviert. So laedt man nie versehentlich doppelt hoch.

### Debug & Logs

Falls etwas nicht funktioniert:

1. Gehe zu **"Debug & Logs"** in der Sidebar
2. Dort siehst du alle Log-Nachrichten in Echtzeit
3. Fehler sind rot markiert
4. Klicke auf **"Error-Log"** um die Fehlerdatei herunterzuladen
5. Oder **"Komplettes Log"** fuer alle Details

Die Log-Dateien findest du auch manuell:
- Windows: `backend\storage\logs\3d-uploader.log`
- macOS (App): `~/.3d-uploader/logs/3d-uploader.log`

### Session-Verwaltung

- Sessions werden automatisch gespeichert
- Pruefe ob eine Session noch gueltig ist: Einstellungen > "Pruefen"
- Abgelaufene Sessions: Einfach erneut einloggen
- Ausloggen: Einstellungen > "Ausloggen" (loescht gespeicherte Session)

---

## Haeufige Probleme

### Upload schlaegt fehl

1. Pruefe ob du eingeloggt bist (Einstellungen > "Pruefen")
2. Schaue ins Error-Log (Debug & Logs > "Error-Log")
3. Die Plattform hat moeglicherweise ihre Seite geaendert –
   dann muessen die Upload-Selektoren angepasst werden

### Browser oeffnet sich nicht beim Login

Stelle sicher dass Playwright Chromium installiert ist.

**Windows:**
```
.venv\Scripts\activate.bat
python -m playwright install chromium
```

**macOS:**
```bash
source .venv/bin/activate
python -m playwright install chromium
```

### Port 8100 ist belegt

**Windows:**
```
netstat -ano | findstr :8100
taskkill /PID <PID> /F
```

**macOS:**
```bash
lsof -i :8100
kill -9 <PID>
```

---

## Technische Details

| Komponente | Technologie |
|-----------|-------------|
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend | React, TypeScript, Tailwind CSS, Vite |
| Upload-Automatisierung | Playwright (Chromium) |
| Daten | Lokal in `backend/storage/` |
| Port | 8100 |
