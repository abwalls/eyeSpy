from typing import Optional
from pydantic import BaseModel

class CameraBase(BaseModel):
    name: str
    url: str
    output: Optional[str] = None
    fps: float = 20.0

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    output: Optional[str] = None
    fps: Optional[float] = None

class Camera(CameraBase):
    id: int

    class Config:
        orm_mode = True
