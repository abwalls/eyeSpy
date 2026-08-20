# eyeSpy

Custom Surveillance Storage Solution

This project provides a basic scaffold for aggregating multiple surveillance
camera feeds and storing the footage locally. It relies on OpenCV for
processing video streams and writes recordings to your hard drive to avoid
cloud storage fees.

## Requirements

- Python 3.8+
- [OpenCV](https://opencv.org/) (installed via `opencv-python-headless`)
- [PyYAML](https://pyyaml.org/) for configuration parsing

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

Camera feeds are defined in `cameras.yaml`:

```yaml
cameras:
  - name: camera1
    url: rtsp://user:pass@192.168.1.10:554/stream1
    output: recordings/camera1
    fps: 20.0
```

Add one entry per camera. The output directory will be created if it does not
exist.

## Authentication

The camera API requires an API key. Set `EYESPY_API_KEY` in your environment
(or `.env` file), then pass it on every request via the `X-API-Key` header:

```bash
export EYESPY_API_KEY=change-me
curl -H "X-API-Key: change-me" http://127.0.0.1:8000/cameras/
```

The server binds to `127.0.0.1` by default. Set `EYESPY_HOST=0.0.0.0` only if
you intend to expose it beyond localhost, and put it behind your own network
controls if you do.

Camera URLs are restricted to `rtsp://`/`rtsps://` schemes to prevent the
`/cameras/{id}/test` endpoint from being used to probe arbitrary hosts.

## Running

Run the API server with:

```bash
python main.py --config cameras.yaml
```
To start the background worker that records camera streams run:

```
python -m eyespy.worker
```


The application will start recording each configured feed. Stop it with
`Ctrl+C`. Footage is saved in the directories specified in the configuration
file.

## Testing Camera Feeds

The API exposes an endpoint to verify that a configured camera feed is
reachable. Use `/cameras/<id>/test` to check the connection for a specific
camera by ID. A successful response will include `{"status": "success"}` while
failures return an error message.
