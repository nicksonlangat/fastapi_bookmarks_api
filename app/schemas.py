from pydantic import BaseModel

class OGMetadataBase(BaseModel):
    url: str

class OGMetadataCreate(OGMetadataBase):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None

class OGMetadataResponse(OGMetadataBase):
    id: int
    title: str | None
    description: str | None
    image_url: str | None

    class Config:
        orm_mode = True