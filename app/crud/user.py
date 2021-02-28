from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, Union

from app.models import models
from app.schemas.User import UserCreate, UserUpdate,User
from app.core.security import get_password_hash, verify_password
from uuid import UUID
import bcrypt
from app.core.config import settings

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.isdeleted == False and models.User.isactive == True).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, id:UUID):
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_email(db: Session, email:str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_super_user(db: Session, user: UserCreate, user_id: UUID = settings.FIRST_SUPERUSER_ID):
    hashed_password =get_password_hash(user.password.encode('utf-8'))
    db_user = models.User(id = user_id,createdby=user_id, modifiedby=user_id,
                            hashed_password = hashed_password,email = user.email,
                            full_name=user.full_name,is_active=user.is_active,is_superuser=user.is_superuser)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user(db: Session, user: UserCreate, user_id: UUID = settings.FIRST_SUPERUSER_ID):
    hashed_password =get_password_hash(user.password.encode('utf-8'))
    db_user = models.User(createdby=user_id, modifiedby=user_id,
                            hashed_password = hashed_password,email = user.email,
                            full_name=user.full_name,is_active=user.is_active,is_superuser=user.is_superuser)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: UserUpdate, id: UUID, user_id: UUID = settings.FIRST_SUPERUSER_ID):
    hashed_password =get_password_hash(user.hashed_password.encode('utf-8'))
    user.hashed_password = hashed_password
    updateData = user.dict(exclude_unset=True)
    updateData['modifiedby'] = user_id
    db.query(models.User).filter(models.User.id == id).update(updateData)
    db.commit()

    return db.query(models.User).filter(models.User.id == id).first()

def delete_user(db: Session, id: UUID, user_id: UUID = settings.FIRST_SUPERUSER_ID):
    db.query(models.User).filter(models.User.id == id).update({'isdeleted':True})
    db.commit()
    return db.query(models.User).filter(models.User.id == id).first()

def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password.encode('utf-8'), user.hashed_password):
        return None
    return user

def is_active(user: User) -> bool:
        return user.is_active