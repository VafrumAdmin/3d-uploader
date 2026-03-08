from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from playwright.async_api import BrowserContext

from models.model3d import Model3D


class BaseUploader(ABC):
    @abstractmethod
    async def upload_model(
        self,
        context: BrowserContext,
        model: Model3D,
        on_progress: Callable[[str, int], Awaitable[None]],
    ) -> str | None:
        """
        Lädt ein Modell auf die Plattform hoch.
        Gibt die URL zum hochgeladenen Modell zurück.
        """
        ...
