from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.datastructures import URL
from cachetools import TTLCache, cached
from postgrest.base_request_builder import APIResponse
from datetime import timedelta
from .. import schemas, models, dependencies
from ..instance.config import get_settings
from ..rate_limiter import rate_limiter


url_shortener = APIRouter()
cache = TTLCache(maxsize=100, ttl=300)


def get_admin_info(url: models.URL) -> schemas.URL_Info:
    base_url = URL(get_settings().base_url)
    admin_endpoint = url_shortener.url_path_for(
        "administration info", secret_key=url.secret_key
    )
    return schemas.URL_Info(
        target_url=url.target_url,
        is_active=url.is_active,
        clicks=url.clicks,
        shortened_url=str(base_url.replace(path=url.key)),
        admin_url=str(base_url.replace(path=admin_endpoint))
    )


# - - - - - - - - - - - SHORTEN URL - - - - - - - - - - -
# paste long urls to shorten
@url_shortener.post("/shorten-url", response_model=schemas.URL_Info)
async def shorten_url(url: schemas.User_URL):
    # validate url
    """
    Shortens a given URL and returns administrative information.

    This endpoint receives a URL, validates it, and if valid, creates a shortened version of the URL.
    It then returns the shortened URL along with administrative details, such as an admin URL.

    Args:
        url: The original URL to be shortened, encapsulated in a User_URL schema.

    Returns:
        A URL_Info schema containing the target URL, its shortened version, and admin details.

    Raises:
        HTTPException: If the provided URL is invalid.
    """
    if not dependencies.validate_url(url.target_url):
        dependencies.raise_bad_request("Your provided URL is invalid, please insert a valid URL.")
    
    new_url = dependencies.create_new_url(url.target_url)
    return get_admin_info(new_url)


# - - - - - - - - - - - CUSTOMIZE URL ADDRESS - - - - - - - - - - -
# customize address of shortened url
@url_shortener.put("/{url_key}", response_model=schemas.URL_Info)
async def customize_short_url_address(
    url: str,
    new_address: str,
    request: Request,
    ):
    """
    Customizes the address of a shortened URL.

    Given a shortened URL and a new address, this function will update the shortened URL's address in the database.

    Args:
        url (str): The key of the shortened URL to customize. Either full address: "https://example.com/abc123" or just key: "abc123".

        new_address (str): The new address to assign to the shortened URL.

    Returns:
        The shortened URL, with its new address.

    Raises:
        HTTPException: If the new address already exists in the database.
    """
    if shortened_url := dependencies.customize_short_url_address(url, new_address):
        return get_admin_info(shortened_url)
    dependencies.raise_not_found(request)


# - - - - - - - - - - - GENERATE QR CODE - - - - - - - - - - -
# generate qr code
@url_shortener.get("/{url_key}/qrcode")
@rate_limiter(limit=10, interval=timedelta(seconds=60))
@cached(cache)
async def generate_qr_code(request: Request, url_key: str):
    if '/' in url_key:
        url_key = url_key.split("/")[-1]

    if url_in_db := dependencies.get_shortened_url_by_key(url_key):
        base_url = URL(get_settings().base_url)
        shortened_url = str(base_url.replace(path=url_key))

        qrcode = dependencies.generate_qr_code(shortened_url)

        response = StreamingResponse(content=qrcode, media_type="image/png")
        response.headers["Content-Disposition"] = f"attachment; filename=qr_code_{url_key}.png"
        return response
    dependencies.raise_bad_request("URL not found.")


# - - - - - - - - - - - REDIRECT URL - - - - - - - - - - -
# redirect shortened url to target url
@url_shortener.get("/{url_key}")
@rate_limiter(limit=10, interval=timedelta(seconds=60))
@cached(cache)
async def forward_to_target_url(
    request: Request,
    url_key: str
):
    if short_url := dependencies.get_shortened_url_by_key(url_key):
        dependencies.update_db_clicks(short_url)
        return RedirectResponse(short_url.target_url)
    dependencies.raise_not_found(request)


# - - - - - - - - - - - ANALYTICS - - - - - - - - - - -
# get short url analytics
@url_shortener.get("/{url_key}/analytics", response_model=schemas.URL)
@rate_limiter(limit=10, interval=timedelta(seconds=60))
@cached(cache)
async def get_analytics(request: Request, url_key: str):
    if short_url := dependencies.get_url_analysis(url_key):
        return schemas.URL(
            target_url=short_url.target_url,
            is_active=short_url.is_active,
            clicks=short_url.clicks
        )
    dependencies.raise_not_found(request)


# - - - - - - - - - - - ADMINISTRATION - - - - - - - - - - -
# get information about shortened url
@url_shortener.get(
        "/admin/{secret_key}",
        name="administration info",
        response_model=schemas.URL_Info
    )
@cached(cache)
async def url_info(secret_key: str, request: Request):
    if url := dependencies.get_shortened_url_by_secret_key(secret_key):
        return get_admin_info(url)
    dependencies.raise_not_found(request)


# - - - - - - - - - - - DELETE URL - - - - - - - - - - -
# delete shortened url
@url_shortener.delete("/{url_key}/delete")
async def delete_url(
    url_key: str,
    request: Request
):
    if url := dependencies.deactivate_url_by_url_key(url_key):
        message = f"Successfully deleted shortened url for {url.target_url}"
        return {"detail": message}
    dependencies.raise_not_found(request)

@url_shortener.put("/{url_key}/recover")
async def recover_url(url_key: str, request: Request):
    if url := dependencies.activate_url_by_url_key(url_key):
        message = f"Successfully recovered deleted url for {url.target_url}"
        return {"detail": message}
    dependencies.raise_not_found(request)

# # danger zone
# @url_shortener.delete("/admin/{secret_key}")
# async def delete_url_by_admin(secret_key: str, request: Request, db: dependencies.db):
#     if url := dependencies.delete_url_by_secret_key(secret_key, db):
#         message = f"Successfully deleted shortened url for {url.target_url}"
#         return {"detail": message}
#     dependencies.raise_not_found(request)
