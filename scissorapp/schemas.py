from pydantic import BaseModel


class User_URL(BaseModel):
    target_url: str

class URL(User_URL):
    is_active: bool
    clicks: int

    class config:
        orm_mode = True

class URL_Info(URL):
    shortened_url: str
    admin_url: str

