from sqlalchemy.orm import Session
import os

from . import models, schemas

VIDEO_STORAGE_PATH = os.getenv("VIDEO_STORAGE_PATH", "recordings")


def get_camera(db: Session, camera_id: int):
    return db.query(models.Camera).filter(models.Camera.id == camera_id).first()


def get_camera_by_name(db: Session, name: str):
    return db.query(models.Camera).filter(models.Camera.name == name).first()


def get_cameras(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Camera).offset(skip).limit(limit).all()


def create_camera(db: Session, camera: schemas.CameraCreate):
    data = camera.dict()
    if not data.get("output"):
        data["output"] = VIDEO_STORAGE_PATH
    db_camera = models.Camera(**data)
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def update_camera(db: Session, camera_id: int, camera: schemas.CameraUpdate):
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return None
    for field, value in camera.dict(exclude_unset=True).items():
        setattr(db_camera, field, value)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def delete_camera(db: Session, camera_id: int):
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return None
    db.delete(db_camera)
    db.commit()
    return db_camera
