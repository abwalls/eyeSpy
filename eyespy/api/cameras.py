from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


@router.get("/{camera_id}/test", response_model=schemas.CameraTestResult)
def test_camera_feed(camera_id: int, db: Session = Depends(get_db)):
    """Validate that the camera's RTSP stream can be opened."""
    cam = crud.get_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    import cv2

    cap = cv2.VideoCapture(cam.url)
    try:
        if not cap.isOpened():
            return {"ok": False, "error": "Unable to open stream"}
        ret, _ = cap.read()
        if not ret:
            return {"ok": False, "error": "Unable to read frame from stream"}
        return {"ok": True, "error": None}
    finally:
        cap.release()
