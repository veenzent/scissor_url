from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.datastructures import URL
from scissorapp import schemas, models, dependencies
from ..instance.config import get_settings


url_shortener = APIRouter()


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
async def shorten_url(url: schemas.User_URL, db: dependencies.db):
    # validate url
    if not dependencies.validate_url(url.target_url):
        dependencies.raise_bad_request("Your provided URL is invalid, please insert a valid URL.")
    
    new_url = dependencies.create_new_url(db, url)
    return get_admin_info(new_url)


# - - - - - - - - - - - CUSTOMIZE URL ADDRESS - - - - - - - - - - -
# customize address of shortened url
@url_shortener.put("/{url_key}", response_model=schemas.URL_Info)
async def customize_short_url_address(
    url_key: str,
    new_address,
    request: Request,
    db: dependencies.db
    ):
    if shortened_url := dependencies.customize_short_url_address(url_key, new_address, db):
        return get_admin_info(shortened_url)
    dependencies.raise_not_found(request)


# - - - - - - - - - - - SHARE URL - - - - - - - - - - -
# share shortened url on socail media


# generate qr code
@url_shortener.get("/{url_key}/share")
async def generate_qr_code(url_key: str):
    base_url = URL(get_settings().base_url)
    shortened_url = str(base_url.replace(path=url_key))

    qrcode = dependencies.generate_qr_code(shortened_url)

    response = StreamingResponse(content=qrcode, media_type="image/png")
    response.headers["Content-Disposition"] = f"attachment; filename=qr_code_{url_key}.png"
    return response

# download qr code
@url_shortener.get("/download-qr-code")
async def download_qr_code():
    pass




# - - - - - - - - - - - REDIRECT URL - - - - - - - - - - -
# redirect shortened url to target url
@url_shortener.get("/{url_key}")
async def forward_to_target_url(
    url_key: str,
    request: Request,
    db: dependencies.db
):
    if short_url := dependencies.get_shortened_url_by_key(url_key, db):
        dependencies.update_db_clicks(short_url, db)
        return RedirectResponse(short_url.target_url)
    dependencies.raise_not_found(request)


# - - - - - - - - - - - ADMINISTRATION - - - - - - - - - - -
# get information about shortened url
@url_shortener.get(
        "/admin/{secret_key}",
        name="administration info",
        response_model=schemas.URL_Info
    )
async def url_info(secret_key: str, request: Request, db: dependencies.db):
    if url := dependencies.get_shortened_url_by_secret_key(secret_key, db):
        return get_admin_info(url)
    dependencies.raise_not_found(request)


# - - - - - - - - - - - DELETE URL - - - - - - - - - - -
# delete shortened url
@url_shortener.delete("/admin/{secret_key}")
async def delete_url(
    secret_key: str,
    request: Request,
    db: dependencies.db
):
    if url := dependencies.deactivate_url_by_secret_key(secret_key, db):
        message = f"Successfully deleted shortened url for {url.target_url}"
        return {"detail": message}
    dependencies.raise_not_found(request)









# share shortened url via social media
@url_shortener.get("/share-url")
async def share_shortened_url():
    pass

