from uploaders.base_uploader import BaseUploader
from uploaders.makerworld import MakerWorldUploader
from uploaders.crealitycloud import CrealityCloudUploader
from uploaders.makeronline import MakeronlineUploader

_uploaders: dict[str, BaseUploader] = {
    "makerworld": MakerWorldUploader(),
    "crealitycloud": CrealityCloudUploader(),
    "makeronline": MakeronlineUploader(),
}


def get_uploader(platform: str) -> BaseUploader:
    uploader = _uploaders.get(platform)
    if not uploader:
        raise ValueError(f"Kein Uploader für Plattform: {platform}")
    return uploader
