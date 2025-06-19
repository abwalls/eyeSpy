"""Background worker that records all configured camera streams."""

import signal
import threading
import time
from typing import List

from .database import SessionLocal, engine
from . import crud, models
from .recorder import CameraRecorder

# Global list to hold active recorders
recorders: List[CameraRecorder] = []
# Event to signal shutdown
shutdown_event = threading.Event()


def _signal_handler(signum, frame):
    """Handle termination signals by stopping all recorders."""
    shutdown_event.set()
    for recorder in list(recorders):
        try:
            recorder.stop()
        except Exception:
            # Ignore errors during shutdown
            pass


def run():
    """Load cameras from the database and start recorders."""
    with SessionLocal() as db:
        cameras = crud.get_cameras(db)

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
    """Entry point for the worker when used as a script."""
    # Ensure database tables exist before accessing them
    models.Base.metadata.create_all(bind=engine)
    run()


if __name__ == "__main__":
    main()
