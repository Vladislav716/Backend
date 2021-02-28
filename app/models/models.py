from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, inspect, Table, select
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float
from app.db.database import Base,engine
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL
from sqlalchemy_utils.view import create_view
from sqlalchemy_utils.view import CreateView
from sqlalchemy.ext import compiler
from datetime import datetime
from sqlalchemy_utils import TSVectorType


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, index=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    createdby = Column(GUID, ForeignKey("users.id"))
    createddate = Column(DateTime, default=datetime.now)
    modifiedby = Column(GUID, ForeignKey("users.id"))
    modifieddate = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    isdeleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=True)
    search_vector = Column(TSVectorType("email","full_name")) 





users = Table('users',Base.metadata,autoload=True,auto_load_with=engine)


    