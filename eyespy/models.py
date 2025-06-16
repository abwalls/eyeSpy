from sqlalchemy import Column, Integer, String, Float

from .database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    output = Column(String, nullable=False)
    fps = Column(Float, default=20.0)
