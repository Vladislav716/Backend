from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models import models

from app.schemas.Token import Token, TokenPayload

from app import crud, schemas
from app.core import security
from app.core.config import settings
from app.db.database import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    #tokenUrl=f"{settings.API_V1_STR}/login/access-token"
    tokenUrl = 'http://127.0.0.1:8000/user/access-token'
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        userid: str = payload.get("sub")
        if userid is None:
            raise credentials_exception
        token_data = TokenPayload(sub=userid)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get_user_by_id(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


