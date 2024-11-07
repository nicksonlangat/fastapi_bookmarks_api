from urllib.parse import urljoin
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from . import models, schemas, crud
from .database import engine, get_db


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://bookmarks.nicklangat.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows requests from specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Create the database tables
models.Base.metadata.create_all(bind=engine)


# Function to fetch OG metadata from a URL
def fetch_og_metadata(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to fetch URL")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get OG metadata
    title_tag = soup.find('meta', property='og:title')
    description_tag = soup.find('meta', property='og:description')
    image_tag = soup.find('meta', property='og:image')

    # Get fallback title and description from the <title> and <meta name="description">
    title = title_tag['content'] if title_tag and title_tag.has_attr('content') else soup.title.string or 'Untitled'
    description = description_tag['content'] if description_tag and description_tag.has_attr('content') else \
                  soup.find('meta', attrs={"name": "description"})['content'] if soup.find('meta', attrs={"name": "description"}) else 'No description available'

    # Get the logo from favicon or first image
    favicon_tag = soup.find('link', rel='icon')
    logo = urljoin(url, favicon_tag['href']) if favicon_tag and favicon_tag.has_attr('href') else \
           image_tag['content'] if image_tag and image_tag.has_attr('content') else ''

    return {
        "title": title,
        "description": description,
        "image_url": logo
    }



@app.post("/add-bookmarks/", response_model=schemas.OGMetadataResponse)
def create_og_metadata(og_data: schemas.OGMetadataBase, db: Session = Depends(get_db)):
    # Check if metadata for the URL already exists
    db_metadata = crud.get_og_metadata_by_url(db, url=og_data.url)
    if db_metadata:
        return db_metadata
    
    # Fetch OG metadata
    metadata = fetch_og_metadata(og_data.url)
    
    # Save to the database
    og_metadata = schemas.OGMetadataCreate(url=og_data.url, **metadata)
    return crud.create_og_metadata(db=db, metadata=og_metadata)


@app.get("/get-bookmarks/", response_model=list[schemas.OGMetadataResponse])
def read_all_og_metadata(db: Session = Depends(get_db)):
    bookmarks = crud.get_all_og_metadata(db)
    return bookmarks

@app.delete("/delete-bookmark/{id}", response_model=schemas.OGMetadataResponse)
def delete_og_metadata(id: int, db: Session = Depends(get_db)):
    deleted_metadata = crud.delete_og_metadata(db, id=id)
    if not deleted_metadata:
        raise HTTPException(status_code=404, detail="OG metadata not found")
    return deleted_metadata