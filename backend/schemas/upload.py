from pydantic import BaseModel


class UploadRequest(BaseModel):
    model_id: str
    platforms: list[str]


class UploadRetryRequest(BaseModel):
    upload_id: str
