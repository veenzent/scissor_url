from pydantic import BaseModel

class URL(BaseModel):
    id: str
    target_url: str
    key: str
    secret_key: str
    is_active: str
    clicks: str

    class Config:
        from_attributes = True