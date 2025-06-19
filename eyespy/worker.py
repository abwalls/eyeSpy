"""Background worker that records all configured camera streams."""

import signal
import threading
import time
from typing import List

# Allow running as a script by ensuring the package root is on the path
if __package__ in (None, ""):
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from eyespy import crud, models
from eyespy.database import SessionLocal, engine
from eyespy.recorder import CameraRecorder

# Active recorders
recorders: List[CameraRecorder] = []
# Event to coordinate shutdown across threads
shutdown_event = threading.Event()


def _stop_all() -> None:
    """Stop all active recorders, ignoring any errors."""
    for rec in list(recorders):
        try:
            rec.stop()
        except Exception:
            pass


def _signal_handler(signum, frame) -> None:
    """Handle termination signals by stopping all recorders."""
    shutdown_event.set()
    _stop_all()


def run() -> None:
    """Load cameras from the database and start recording."""
    # Ensure database tables exist when running as a script
    models.Base.metadata.create_all(bind=engine)

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
        _stop_all()


def main() -> None:
    """Entry point for the worker when run as a script."""
    run()


if __name__ == "__main__":
    main()
