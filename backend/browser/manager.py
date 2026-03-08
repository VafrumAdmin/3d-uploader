import asyncio
import shutil
from pathlib import Path

from playwright.async_api import async_playwright, Playwright, Browser

from config import SESSIONS_DIR


class BrowserManager:
    def __init__(self):
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def _ensure_playwright(self):
        if not self._playwright:
            self._playwright = await async_playwright().start()

    def get_session_path(self, platform: str) -> Path:
        return SESSIONS_DIR / platform

    async def open_login_browser(self, platform: str, login_url: str) -> str | None:
        """Öffnet sichtbaren Browser für manuellen Login. Gibt Username zurück."""
        await self._ensure_playwright()

        user_data_dir = self.get_session_path(platform)
        user_data_dir.mkdir(parents=True, exist_ok=True)

        context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"],
        )

        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(login_url, wait_until="domcontentloaded")

        # Warte bis der User das Browser-Fenster schließt
        try:
            await page.wait_for_event("close", timeout=300_000)  # 5 Minuten max
        except Exception:
            pass

        # Speichere State
        state_path = user_data_dir / "state.json"
        try:
            await context.storage_state(path=str(state_path))
        except Exception:
            pass

        await context.close()
        return None

    async def get_upload_context(self, platform: str):
        """Gibt einen Browser-Context mit gespeicherter Session zurück."""
        await self._ensure_playwright()

        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )

        state_path = self.get_session_path(platform) / "state.json"
        if state_path.exists():
            context = await self._browser.new_context(
                storage_state=str(state_path),
                viewport={"width": 1280, "height": 800},
            )
        else:
            context = await self._browser.new_context(
                viewport={"width": 1280, "height": 800},
            )

        return context

    async def check_session(self, platform: str, login_url: str) -> bool:
        """Prüft ob die gespeicherte Session noch gültig ist."""
        state_path = self.get_session_path(platform) / "state.json"
        if not state_path.exists():
            return False

        try:
            context = await self.get_upload_context(platform)
            page = await context.new_page()
            await page.goto(login_url, wait_until="domcontentloaded", timeout=15_000)
            await asyncio.sleep(2)

            # Plattformspezifische Login-Checks
            is_logged_in = False
            if platform == "makerworld":
                # Prüfe ob Avatar/Profil-Element sichtbar ist
                is_logged_in = await page.locator('[class*="avatar"], [class*="user-info"], [href*="/u/"]').count() > 0
            elif platform == "crealitycloud":
                is_logged_in = await page.locator('[class*="avatar"], [class*="user"], [class*="profile"]').count() > 0
            elif platform == "makeronline":
                is_logged_in = await page.locator('[class*="avatar"], [class*="user"], [class*="profile"]').count() > 0

            await page.close()
            await context.close()
            return is_logged_in
        except Exception:
            return False

    async def clear_session(self, platform: str):
        """Löscht gespeicherte Session."""
        session_path = self.get_session_path(platform)
        if session_path.exists():
            shutil.rmtree(session_path, ignore_errors=True)

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()


browser_manager = BrowserManager()
