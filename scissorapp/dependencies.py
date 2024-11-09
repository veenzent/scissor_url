import secrets, string
from urllib.parse import urlparse
from urllib.request import urlopen
from typing import Annotated
from fastapi import HTTPException, Request, status, Depends
from io import BytesIO
import segno
from functools import wraps
import time
from .database import supabase
from . import schemas, models


# - - - - - - - - DATABASE INTERACTIONS - - - - - - - -
def get_shortened_url_by_key(url_key: str) -> models.URL:
    shortened_url = supabase.table("urls")\
        .select("key").eq("key", url_key).execute()
    
    url_active = supabase.table("urls")\
        .select("is_active").eq("is_active", True).execute()
    
    if url_active and shortened_url:
        return shortened_url

def get_shortened_url_by_secret_key(secret_key: str) -> models.URL:
    if shortened_url := supabase.table("urls")\
        .select("secret_key").eq("secret_key", secret_key).execute():
        return shortened_url

def create_new_url(url: str) -> models.URL:
    key = create_random_unique_key()
    secret_key = f"{key}_{create_random_key(8)}"
    new_url = models.URL(target_url=url, key=key, secret_key=secret_key)

    supabase.table("urls").insert(new_url.model_dump()).execute()
    return new_url


# - - - - - - - - OTHER INTERACTIONS - - - - - - - -
def create_random_key(length: int = 5) -> str:
    chars = string.ascii_letters + string.digits
    key = "".join(secrets.choice(chars) for _ in range(length))
    return key

def create_random_unique_key():
    unique_key = create_random_key()
    while get_shortened_url_by_key(unique_key):
        unique_key = create_random_key()
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

# def update_db_clicks(url: schemas.URL, db: db) -> models.URL:
#     url.clicks += 1
#     db.commit()
#     db.refresh(url)
#     return url

# def deactivate_url_by_url_key(url_key: str, db: db) -> models.URL:
#     if url := get_shortened_url_by_key(url_key, db):
#         url.is_active = False
#         db.commit()
#         db.refresh(url)
#         return url

# def activate_url_by_url_key(url_key: str, db: db) -> models.URL:
#     if url := db.query(models.URL).filter(models.URL.key == url_key).first():
#         url.is_active = True
#         db.commit()
#         db.refresh(url)
#         return url

# def delete_url_by_secret_key(secret_key: str, db: db) -> models.URL:
#     if url := db.query(models.URL).filter(models.URL.secret_key == secret_key).first():
#         db.delete(url)
#         db.commit()
#         db.refresh(url)
#         return url

# def customize_short_url_address(url_key: str, new_address, db: db) -> models.URL:
#     if short_url := get_shortened_url_by_key(url_key, db):
#         # check if new address is already
#         if new_address_in_db := get_shortened_url_by_key(new_address, db):
#                 raise_bad_request(f"URL address: {new_address} already exists")

#         # update address
#         short_url.key = new_address
#         db.commit()
#         db.refresh(short_url)
#         return short_url

# def generate_qr_code(data: str):
#     image_buffer = BytesIO()

#     qrcode = segno.make_qr(data)
#     qrcode.save(
#         image_buffer,
#         kind="png",
#         scale=5,
#         border=3,
#         light="cyan",
#         dark="darkblue"
#     )

#     image_buffer.seek(0)
#     return image_buffer

# def get_url_analysis(url: str, db:db):
#     if url := get_shortened_url_by_key(url, db):
#         return url