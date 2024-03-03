from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    env_name: str = "local"
    base_url: str = "http://localhost:8000"
    database_url: str = "postgresql://username:password@localhost/scissor_url_db"
    test_database_url: str = "postgresql://username:password@localhost/scissor_url_db"

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    print(f"BASE_URL: ", settings.base_url)
    print(f"DATABASE_URL: {settings.database_url}")
    return settings

# print("ENV_NAME: ", get_settings().env_name)
# print("BASE_URL: ", get_settings().base_url)
# print("DATABASE_URL: ", get_settings().database_url)
