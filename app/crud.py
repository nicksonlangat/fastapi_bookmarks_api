from sqlalchemy.orm import Session
from . import models, schemas

def create_og_metadata(db: Session, metadata: schemas.OGMetadataCreate):
    db_metadata = models.OGMetadata(**metadata.dict())
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata

def get_og_metadata_by_url(db: Session, url: str):
    return db.query(models.OGMetadata).filter(models.OGMetadata.url == url).first()

def get_all_og_metadata(db: Session):
    return db.query(models.OGMetadata).order_by(models.OGMetadata.id.desc()).all()

def delete_og_metadata(db: Session, id: int):
    db_metadata = db.query(models.OGMetadata).filter(models.OGMetadata.id == id).first()
    if db_metadata:
        db.delete(db_metadata)
        db.commit()
        return db_metadata
    return None