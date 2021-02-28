import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
from uuid import UUID

class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/TestDB"
    FIRST_SUPERUSER_ID: str = "234cdf6d-bf79-44e9-9617-efd0d11e870e"
    FIRST_SUPERUSER: str = "SuperUser"
    FRIST_SUPERUER_EMAIL: str = "superuser@email.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123456"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://127.0.0.1:8000","http://localhost:8080/",\
        "http://localhost:8000","http://127.0.0.1:8080/"]

    
    EMAILS_FROM_NAME = ''
    EMAILS_FROM_EMAIL = ''
    SMTP_USER = ''
    SMTP_HOST = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_TLS = True
    SMTP_PASSWORD = ''
    EMAIL_RESET_TOKEN_EXPIRE_HOURS = 1
    EMAILS_ENABLED = SMTP_HOST and SMTP_PORT and EMAILS_FROM_EMAIL


    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings()