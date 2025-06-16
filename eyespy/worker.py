"""Background worker that records all configured camera streams."""

import signal
import threading
import time
from typing import List

from eyespy.database import SessionLocal, engine
from . import crud, models
from .recorder import CameraRecorder

# Ensure database tables exist
models.Base.metadata.create_all(bind=engine)

# Global list to hold active recorders
recorders: List[CameraRecorder] = []
# Event to signal shutdown
shutdown_event = threading.Event()


def _signal_handler(signum, frame):
    """Handle termination signals by stopping all recorders."""
    shutdown_event.set()
    for recorder in recorders:
        try:
            recorder.stop()
        except Exception:
            pass


def run():
    """Load cameras from the database and start recorders."""
    db = SessionLocal()
    try:
        cameras = crud.get_cameras(db)
    finally:
        db.close()

    for cam in cameras:
        rec = CameraRecorder(cam.name, cam.url, cam.output, fps=cam.fps)
        rec.start()
        recorders.append(rec)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    finally:
        _signal_handler(None, None)


def main():
    run()


if __name__ == "__main__":
    main()
