import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
from uuid import UUID

class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DATABASE_URL: str = "postgresql://postgres:qwe123qwe@localhost:5432/testDB"
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
    GOOGLE = "google-oidc"
    AZURE = "azure-oidc"

    GOOGLE_CLIENT_ID = "199230757330-q8rkbiijlpc7mg9u4n23usd8lbqgg1if.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "Ob6IyfcX29qkQmoptfL6c1bo"
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_REDIRECT_URL = "http://localhost:8000/google-login-callback/"

    # Azure login
    AZURE_CLIENT_ID = "aa0eaf54-8820-4126-a16f-a340f327bc43"
    AZURE_CLIENT_SECRET = "0948a3d3-62eb-4447-967b-3690b4be723d"
    AZURE_TENANT_ID = "f8cdef31-a31e-4b4a-93e4-5f571e91255a"
    AZURE_AUTHORITY = f"https://login.microsoftonline.com/common"
    AZURE_DISCOVERY_URL = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
    AZURE_REDIRECT_URL = "http://localhost:8000/azure-login-callback/"

    FRONTEND_URL = "http://localhost:8080"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings()