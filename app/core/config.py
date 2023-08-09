import os
from functools import lru_cache
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: Optional[int] = 3306
    DB_USER: Optional[str] = "root"
    DB_PASSWORD: str
    DB_NAME: Optional[str] = "spending_mannager"

    SQLALCHEMY_DATABASE_URL: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URL")
    def validate_db_url(cls, v, values):
        if not v:
            SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{values['DB_USER']}:{values['DB_PASSWORD']}@{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        return SQLALCHEMY_DATABASE_URL

    SECURITY_ALGORITHM: Optional[str] = "HS256"
    SECRET_KEY: str

    class Config:
        env_file = f'.env.{os.getenv("ENV")}' if os.getenv("ENV") else ".env"


settings = Settings()
