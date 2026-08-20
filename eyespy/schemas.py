from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, validator

ALLOWED_CAMERA_URL_SCHEMES = {"rtsp", "rtsps"}


def _validate_camera_url(url: str) -> str:
    scheme = urlparse(url).scheme.lower()
    if scheme not in ALLOWED_CAMERA_URL_SCHEMES:
        raise ValueError(
            f"camera url must use one of {sorted(ALLOWED_CAMERA_URL_SCHEMES)}, got {scheme!r}"
        )
    return url


class CameraBase(BaseModel):
    name: str
    url: str
    output: Optional[str] = None
    fps: float = 20.0

    _validate_url = validator("url", allow_reuse=True)(_validate_camera_url)

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    output: Optional[str] = None
    fps: Optional[float] = None

    _validate_url = validator("url", allow_reuse=True)(
        lambda v: _validate_camera_url(v) if v is not None else v
    )

class Camera(CameraBase):
    id: int

    class Config:
        orm_mode = True
