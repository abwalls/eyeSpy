import cv2
import threading
import datetime
import os

class CameraRecorder:
    def __init__(self, name, stream_url, output_dir, fourcc='XVID', fps=20.0):
        self.name = name
        self.stream_url = stream_url
        self.output_dir = output_dir
        self.fps = fps
        self.capture = None
        self.writer = None
        self.thread = None
        self.running = False
        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)

    def start(self):
        if self.running:
            return
        os.makedirs(self.output_dir, exist_ok=True)
        self.capture = cv2.VideoCapture(self.stream_url)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.name}_{timestamp}.avi"
        if not self.capture.isOpened():
            raise RuntimeError(f"Failed to open stream: {self.stream_url}")
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.writer = cv2.VideoWriter(
            os.path.join(self.output_dir, filename),
            self.fourcc,
            self.fps,
            (width, height))
        self.running = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.capture:
            self.capture.release()
        if self.writer:
            self.writer.release()

    def _record(self):
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                break
            self.writer.write(frame)
        self.stop()
