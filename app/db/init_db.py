from sqlalchemy.orm import Session
import app.crud.user as cruduser
from app.schemas.User import UserCreate
from app.core.config import settings
import json

def read_countries():
    with open('data/countries.json') as stream:
        countries = json.load(stream)
    return countries

def read_states():
    with open('data/states.json') as stream:
        states = json.load(stream)
    return states

async def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = cruduser.get_user_by_email(db, email=settings.FRIST_SUPERUER_EMAIL)
    if not user:
        user_in = UserCreate(
            full_name=settings.FIRST_SUPERUSER,
            email=settings.FRIST_SUPERUER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=1,
            is_superuser = 1
        )
        user = cruduser.create_super_user(db, user=user_in)
    



async def update_database(db: Session):
    with open('app/data/users.json') as stream: # Insert Country, State, City by checking duplicates, with related values
        useritems = json.load(stream)
        for useritem in useritems:
            user = cruduser.get_user_by_email(db, email=useritem['email'])
            if not user:       
                user_in = UserCreate(email=useritem['email'],full_name=useritem['password'],password=useritem['password'],)
                user = cruduser.create_user(db, user=user_in)
           
