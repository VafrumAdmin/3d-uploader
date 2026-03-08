"""
Einstiegspunkt fuer die gepackte App.
Startet den Uvicorn-Server und oeffnet den Browser.
"""
import sys
import os

# Wenn gepackt, fuege das Bundle-Verzeichnis zum Python-Path hinzu
if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
    os.chdir(bundle_dir)

# Backend-Verzeichnis muss im Path sein
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if os.path.exists(backend_dir):
    sys.path.insert(0, backend_dir)

import uvicorn


def main():
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8100,
        log_level="info",
    )


if __name__ == "__main__":
    main()
