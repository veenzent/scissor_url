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
from postgrest.base_request_builder import APIResponse
from . import schemas, models


# - - - - - - - - DATABASE INTERACTIONS - - - - - - - -
def get_shortened_url_by_key(url_key: str) -> models.URL:
    """
    Gets a shortened URL by its key from the database.

    Args:
        url_key: The key of the shortened URL to retrieve.

    Returns:
        The shortened URL if it exists and is active, or None otherwise.
    """
    shortened_url: APIResponse = supabase.table("urls")\
        .select().eq("key", url_key).eq("is_active", True).execute()
    
    if shortened_url.data:
        shortened_url_data = models.URL(
            # id=shortened_url.data[0].get("id"),
            target_url=shortened_url.data[0].get("target_url"),
            key=shortened_url.data[0].get("key"),
            secret_key=shortened_url.data[0].get("secret_key"),
            is_active=shortened_url.data[0].get("is_active"),
            clicks=shortened_url.data[0].get("clicks")
        )
        return shortened_url_data

    return None

def get_shortened_url_by_secret_key(secret_key: str) -> models.URL:
    if shortened_url := supabase.table("urls")\
        .select("secret_key").eq("secret_key", secret_key).execute():
        return shortened_url
    shortened_url: APIResponse = supabase.table("urls")\
        .select("secret_key").eq("secret_key", secret_key).execute()
    
    if shortened_url.data:
        shortened_url_data = models.URL(
            # id=shortened_url.data[0].get("id"),
            target_url=shortened_url.data[0].get("target_url"),
            key=shortened_url.data[0].get("key"),
            secret_key=shortened_url.data[0].get("secret_key"),
            is_active=shortened_url.data[0].get("is_active"),
            clicks=shortened_url.data[0].get("clicks")
        )
        return shortened_url_data.model_dump()

def create_random_key(length: int = 5) -> str:
    chars = string.ascii_letters + string.digits
    key = "".join(secrets.choice(chars) for _ in range(length))
    return key

def create_random_unique_key():
    unique_key = create_random_key()
    while get_shortened_url_by_key(unique_key):
        unique_key = create_random_key()
    return unique_key

def create_new_url(url: str) -> models.URL:
    key = create_random_unique_key()
    secret_key = f"{key}_{create_random_key(8)}"

    supabase.table("urls")\
        .insert({
            "target_url": url,
            "key": key,
            "secret_key": secret_key
        }).execute()

    new_url = models.URL(
        target_url=url,
        key=key,
        secret_key=secret_key,
        is_active=True,
        clicks=0
    )

    return new_url


# - - - - - - - - OTHER INTERACTIONS - - - - - - - -

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

def update_db_clicks(url: schemas.URL) -> models.URL:
    # increment click
    url.clicks += 1

    # update database
    response = supabase.table("urls")\
            .update({"clicks": url.clicks})\
            .eq("key", url.key)\
            .execute()
    return url

def deactivate_url_by_url_key(url_key: str) -> models.URL:
    if url := get_shortened_url_by_key(url_key):
        url.is_active = False
        response = supabase.table("urls")\
            .update({"is_active": url.is_active})\
            .eq("key", url.key)\
            .execute()
        return url

def activate_url_by_url_key(url_key: str) -> models.URL:
    url: APIResponse = supabase.table("urls")\
        .select().eq("key", url_key).eq("is_active", False).execute()
    
    if url.data:
        url_data = models.URL(
            # id=shortened_url.data[0].get("id"),
            target_url=url.data[0].get("target_url"),
            key=url.data[0].get("key"),
            secret_key=url.data[0].get("secret_key"),
            is_active=url.data[0].get("is_active"),
            clicks=url.data[0].get("clicks")
        )
    
        url_data.is_active = True
        response = supabase.table("urls")\
            .update({"is_active": url_data.is_active})\
            .eq("key", url_data.key)\
            .execute()
        return url_data

# def delete_url_by_secret_key(secret_key: str, db: db) -> models.URL:
#     if url := db.query(models.URL).filter(models.URL.secret_key == secret_key).first():
#         db.delete(url)
#         db.commit()
#         db.refresh(url)
#         return url

def customize_short_url_address(url_key: str, new_address) -> models.URL:
    """
    Customizes the address of a shortened URL.

    Given a shortened URL and a new address, this function will update the
    shortened URL's address in the database.

    Args:
        url_key (str): The key of the shortened URL to customize. Either ful address: "https://example.com/abc123" or just key: "abc123".
        new_address (str): The new address to assign to the shortened URL.

    Returns:
        models.URL: The shortened URL, with its new address.

    Raises:
        HTTPException: If the new address already exists in the database.
    """
    if '/' in url_key:
        url_key = url_key.split("/")[-1]

    if short_url := get_shortened_url_by_key(url_key):
        # check if new address already exists
        if new_address_in_db := get_shortened_url_by_key(new_address):
                raise_bad_request(f"URL address: {new_address} already exists")

        # update address
        short_url.key = new_address
        response = supabase.table("urls")\
            .update({"key": new_address})\
            .eq("key", url_key)\
            .execute()
        # print(response)
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

def get_url_analysis(url: str):
    if url := get_shortened_url_by_key(url):
        return url
