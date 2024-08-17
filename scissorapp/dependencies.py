import secrets, string
from urllib.parse import urlparse
from urllib.request import urlopen
from typing import Annotated
from fastapi import HTTPException, Request, status, Depends
from sqlalchemy.orm import Session
from io import BytesIO
import segno
from functools import wraps
import time
from .database import get_db
from . import schemas, models


# - - - - - - - - DATABASE INTERACTIONS - - - - - - - -
db = get_db()

def get_shortened_url_by_key(url_key: str, db: Session) -> models.URL:
    if shortened_url := db.query(models.URL)\
        .filter(models.URL.key == url_key, models.URL.is_active).first():
        return shortened_url

def get_shortened_url_by_secret_key(secret_key: str, db: Session) -> models.URL:
    if shortened_url := db.query(models.URL)\
        .filter(models.URL.secret_key == secret_key, models.URL.is_active).first():
        return shortened_url

def create_new_url(db: db, url: str) -> models.URL:
    key = create_random_unique_key(db)
    secret_key = f"{key}_{create_random_key(8)}"
    new_url = models.URL(target_url=url, key=key, secret_key=secret_key)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url


# - - - - - - - - OTHER INTERACTIONS - - - - - - - -
def create_random_key(length: int = 5) -> str:
    chars = string.ascii_letters + string.digits
    key = "".join(secrets.choice(chars) for _ in range(length))
    return key

def create_random_unique_key(db: db):
    unique_key = create_random_key()
    while get_shortened_url_by_key(unique_key, db):
        unique_key = create_random_key
    return unique_key

def raise_bad_request(message: str):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request: Request):
    message = f"Entered URL '{request.url}' not found."
    raise HTTPException(status_code=404, detail=message)

def validate_url(url):
    try:
        with urlopen(url) as response:
            if response.status == 200:
                return True
    except Exception as e:
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc and parsed_url.path:
            return True
    return False

def update_db_clicks(url: schemas.URL, db: db) -> models.URL:
    url.clicks += 1
    db.commit()
    db.refresh(url)
    return url

def deactivate_url_by_url_key(url_key: str, db: db) -> models.URL:
    if url := get_shortened_url_by_key(url_key, db):
        url.is_active = False
        db.commit()
        db.refresh(url)
        return url

def activate_url_by_url_key(url_key: str, db: db) -> models.URL:
    if url := db.query(models.URL).filter(models.URL.key == url_key).first():
        url.is_active = True
        db.commit()
        db.refresh(url)
        return url

def delete_url_by_secret_key(secret_key: str, db: db) -> models.URL:
    if url := db.query(models.URL).filter(models.URL.secret_key == secret_key).first():
        db.delete(url)
        db.commit()
        db.refresh(url)
        return url

def customize_short_url_address(url_key: str, new_address, db: db) -> models.URL:
    if short_url := get_shortened_url_by_key(url_key, db):
        # check if new address is already
        if new_address_in_db := get_shortened_url_by_key(new_address, db):
                raise_bad_request(f"URL address: {new_address} already exists")

        # update address
        short_url.key = new_address
        db.commit()
        db.refresh(short_url)
        return short_url

def generate_qr_code(data: str):
    image_buffer = BytesIO()

    qrcode = segno.make_qr(data)
    qrcode.save(
        image_buffer,
        kind="png",
        scale=5,
        border=3,
        light="cyan",
        dark="darkblue"
    )

    image_buffer.seek(0)
    return image_buffer

def get_url_analysis(url: str, db:db):
    if url := get_shortened_url_by_key(url, db):
        return url