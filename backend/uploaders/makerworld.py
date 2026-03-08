import asyncio
import logging
from typing import Callable, Awaitable

from playwright.async_api import BrowserContext

from models.model3d import Model3D
from uploaders.base_uploader import BaseUploader

logger = logging.getLogger(__name__)


class MakerWorldUploader(BaseUploader):
    async def upload_model(
        self,
        context: BrowserContext,
        model: Model3D,
        on_progress: Callable[[str, int], Awaitable[None]],
    ) -> str | None:
        page = await context.new_page()

        try:
            await on_progress("Navigiere zu MakerWorld Upload...", 5)
            await page.goto("https://makerworld.com/en/u/upload", wait_until="domcontentloaded", timeout=30_000)
            await asyncio.sleep(3)

            # --- Schritt 1: Dateien hochladen ---
            await on_progress("Lade 3D-Dateien hoch...", 10)

            # Suche nach File-Input (kann versteckt sein)
            file_input = page.locator('input[type="file"]').first
            file_paths = [f.filepath for f in model.files]
            await file_input.set_input_files(file_paths)
            await asyncio.sleep(3)

            await on_progress("Dateien hochgeladen", 30)

            # --- Schritt 2: Modellname ---
            await on_progress("Fülle Metadaten aus...", 40)

            # Modellname eingeben
            name_input = page.locator('input[placeholder*="name"], input[name*="name"], input[name*="title"]').first
            if await name_input.count() > 0:
                await name_input.clear()
                await name_input.fill(model.name)
                await asyncio.sleep(0.5)

            # --- Schritt 3: Beschreibung ---
            desc_area = page.locator('textarea, [contenteditable="true"], div[class*="editor"]').first
            if await desc_area.count() > 0 and model.description:
                try:
                    await desc_area.click()
                    await desc_area.fill(model.description)
                except Exception:
                    await page.keyboard.type(model.description)
                await asyncio.sleep(0.5)

            await on_progress("Metadaten ausgefüllt", 50)

            # --- Schritt 4: Bilder hochladen ---
            if model.images:
                await on_progress("Lade Bilder hoch...", 60)
                image_inputs = page.locator('input[type="file"][accept*="image"]')
                if await image_inputs.count() > 0:
                    image_paths = [img.filepath for img in model.images]
                    await image_inputs.first.set_input_files(image_paths)
                    await asyncio.sleep(3)

            await on_progress("Bilder hochgeladen", 70)

            # --- Schritt 5: Kategorie auswählen (wenn vorhanden) ---
            if model.category:
                category_selector = page.locator('select, [class*="category"], [class*="select"]').first
                if await category_selector.count() > 0:
                    try:
                        await category_selector.click()
                        await asyncio.sleep(1)
                        option = page.locator(f'text="{model.category}"').first
                        if await option.count() > 0:
                            await option.click()
                    except Exception:
                        pass

            # --- Schritt 6: Lizenz ---
            await on_progress("Setze Lizenz...", 80)

            # --- Schritt 7: Veröffentlichen ---
            await on_progress("Veröffentliche Modell...", 90)

            # Suche nach Submit-Button
            submit_btn = page.locator(
                'button:has-text("Publish"), button:has-text("Submit"), '
                'button:has-text("Upload"), button[type="submit"]'
            ).first

            if await submit_btn.count() > 0:
                await submit_btn.click()
                await asyncio.sleep(5)

            # Versuche die URL des hochgeladenen Modells zu finden
            current_url = page.url
            await on_progress("Upload abgeschlossen!", 100)

            await page.close()
            return current_url

        except Exception as e:
            logger.error(f"MakerWorld Upload-Fehler: {e}")
            # Screenshot für Debugging
            try:
                await page.screenshot(path="storage/debug_makerworld.png")
            except Exception:
                pass
            await page.close()
            raise
