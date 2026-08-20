import os

from fastapi import FastAPI
from dotenv import load_dotenv

from eyespy.api import cameras
from eyespy import models
from eyespy.database import engine

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="eyeSpy API")
app.include_router(cameras.router)

if __name__ == "__main__":
    import uvicorn
    # Defaults to localhost-only; set EYESPY_HOST=0.0.0.0 to expose on the network.
    uvicorn.run(
        "main:app",
        host=os.environ.get("EYESPY_HOST", "127.0.0.1"),
        port=int(os.environ.get("EYESPY_PORT", 8000)),
    )
