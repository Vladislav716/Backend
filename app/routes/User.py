from fastapi import APIRouter
from fastapi import Depends, FastAPI, HTTPException, Body, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from pydantic.networks import EmailStr
from app.routes import deps
from app.crud import user as crud
from app.schemas.Token import Token
from app.schemas.User import UserCreate,User, UserPagination
from app.db.database import SessionLocal, engine, search_filter_sort_paginate
from fastapi_utils.guid_type import GUID
from uuid import UUID
from app.core import security
from typing import Any
from datetime import timedelta
from app.core.config import settings
router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/all/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/{id}/", response_model=User)
def get_user(db: Session = Depends(get_db)):
    return crud.get_user_by_id(db, id=id)

@router.post("/create/", response_model=User)
def create_user(
    user: UserCreate, db: Session = Depends(get_db)
):
    return crud.create_user(db=db, user=user)

@router.put("/update/{id}", response_model=User)
def update_user(
    id:UUID, user: UserCreate, db: Session = Depends(get_db)
):
    return crud.update_user(db=db, user=user, id=id)

@router.delete("/delete/{id}/", response_model=User)
def delete_user(id: UUID, db: Session = Depends(get_db)):
    return crud.delete_user(db, id=id)


@router.post("/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=User)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/", response_model=UserPagination)
def get_users(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy"),
    descending: List[bool] = Query([], alias="descending"),
    fields: List[str] = Query([], alias="field[]"),
    ops: List[str] = Query([], alias="op[]"),
    values: List[str] = Query([], alias="value[]"),
):
    """
    Get all users.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="users",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )