import argparse
import signal
import sys

from eyespy.recorder import CameraRecorder
from eyespy.config import load_config


def main():
    parser = argparse.ArgumentParser(description="Run surveillance camera aggregator")
    parser.add_argument('--config', default='cameras.yaml', help='Path to camera configuration file')
    args = parser.parse_args()

    config = load_config(args.config)
    recorders = []
    for cam in config.get('cameras', []):
        recorder = CameraRecorder(
            name=cam['name'],
            stream_url=cam['url'],
            output_dir=cam.get('output', 'recordings'),
            fps=cam.get('fps', 20.0)
        )
        recorder.start()
        recorders.append(recorder)

    def stop_all(signum, frame):
        for rec in recorders:
            rec.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_all)
    signal.signal(signal.SIGTERM, stop_all)

    signal.pause()


if __name__ == '__main__':
    main()
