from sqlalchemy import Column, Integer, String
from .database import Base

class OGMetadata(Base):
    __tablename__ = "og_metadata"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    