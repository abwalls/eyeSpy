from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import cv2

from .. import crud, schemas, models
from ..database import SessionLocal, engine

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/cameras", tags=["cameras"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.Camera])
def read_cameras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_cameras(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Camera)
def create_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db)):
    db_cam = crud.get_camera_by_name(db, name=camera.name)
    if db_cam:
        raise HTTPException(status_code=400, detail="Camera already exists")
    return crud.create_camera(db, camera)


@router.get("/{camera_id}", response_model=schemas.Camera)
def read_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = crud.get_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam


@router.put("/{camera_id}", response_model=schemas.Camera)
def update_camera(camera_id: int, camera: schemas.CameraUpdate, db: Session = Depends(get_db)):
    cam = crud.update_camera(db, camera_id, camera)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam


@router.delete("/{camera_id}", response_model=schemas.Camera)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = crud.delete_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam


@router.get("/{camera_id}/test")
def test_camera_stream(camera_id: int, db: Session = Depends(get_db)):
    """Check if the RTSP feed for the given camera can be opened."""
    cam = crud.get_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    cap = cv2.VideoCapture(cam.url)
    success = False
    try:
        if cap.isOpened():
            ret, _ = cap.read()
            success = bool(ret)
    finally:
        cap.release()

    return {"camera_id": camera_id, "working": success}
