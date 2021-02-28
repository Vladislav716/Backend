from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

import uvicorn
from app.models import  models
from app.routes.User import router as UserRouter

from app.db.database import SessionLocal, engine
from app.db.init_db import init_db, update_database

from app.core.config import settings
from app.core.utils import send_email
from sqlalchemy_searchable import sync_trigger



import json
from fastapi import FastAPI
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError



models.Base.metadata.create_all(bind=engine)

sync_trigger(engine, "users", "search_vector", ["email","full_name"])

tags_metadata = [
    {"name": "Search", "description": ""},
]


app = FastAPI(
    title="Company Products API",
    openapi_tags=tags_metadata,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
    )

app.add_middleware(SessionMiddleware, secret_key='!secret')

config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Set all CORS enabled origins
'''if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )'''


app.include_router(UserRouter,tags=["User"],prefix="/user")

# Dependency
def get_db():
    db = SessionLocal()
    # init_db(db)
    try:
        yield db
    finally:
        db.close()

''' Async method on startup to load config data'''
@app.on_event("startup")
async def load():    
    await init_db(SessionLocal())
    await update_database(SessionLocal())


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse("/docs")


@app.route('/gsign')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
