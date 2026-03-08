from datetime import datetime
from pydantic import BaseModel


class PlatformInfo(BaseModel):
    key: str
    name: str
    color: str
    login_url: str
    is_logged_in: bool = False
    username: str | None = None
    last_verified: datetime | None = None
