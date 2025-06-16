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
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
