from pydantic import BaseModel

class URL(BaseModel):
    # id: int
    target_url: str
    key: str
    secret_key: str
    is_active: bool
    clicks: int

    class Config:
        from_attributes = True