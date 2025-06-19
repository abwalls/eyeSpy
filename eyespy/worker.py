"""Background worker that records all configured camera streams."""

import signal
import threading
import time
from typing import List

# Ensure the project root is on the import path. This allows running the file
# directly with ``python eyespy/worker.py`` as well as via ``python -m
# eyespy.worker`` without having to continually tweak these imports in future
# pull requests.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eyespy.database import SessionLocal, engine
from eyespy import crud, models
from eyespy.recorder import CameraRecorder

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
