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
from app.core.exceptions import (
    exception_handling,
)
from app.core import security
from app.core.auth_models import ExternalAuthToken
from sqlalchemy_searchable import sync_trigger



import json
from fastapi import FastAPI
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import random
import string

from app.core import (
	providers as auth_providers,
    schemes as auth_schemes,
)
import app.crud.user as cruduser
from app.schemas.User import UserCreate

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

csrf_token_redirect_cookie_scheme = auth_schemes.CSRFTokenRedirectCookieBearer()
auth_token_scheme = auth_schemes.AuthTokenBearer()
access_token_cookie_scheme = auth_schemes.AccessTokenCookieBearer()

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

@app.get("/login-redirect")
async def login_redirect(auth_provider: str):
	""" Redirects the user to the external authentication pop-up

		Args:
			auth_provider: The authentication provider (i.e google-iodc)

		Returns:
			Redirect response to the external provider's auth endpoint
	"""
	async with exception_handling():
		provider = await auth_providers.get_auth_provider(auth_provider)

		request_uri, state_csrf_token = await provider.get_request_uri()
        
		response = RedirectResponse(url=request_uri)
        
		# Make this a secure cookie for production use
		response.set_cookie(key="state", value=f"Bearer {state_csrf_token}", httponly=True)

		return response

@app.get("/google-login-callback/")
async def google_login_callback(
	request: Request,
	_ = Depends(csrf_token_redirect_cookie_scheme)
):
	""" Callback triggered when the user logs in to Google's pop-up.

		Receives an authentication_token from Google which then
		exchanges for an access_token. The latter is used to
		gain user information from Google's userinfo_endpoint.

		Args:
			request: The incoming request as redirected by Google
	"""
	async with exception_handling():
		code = request.query_params.get("code")

		if not code:
			raise AuthorizationException("Missing external authentication token")

		provider = await auth_providers.get_auth_provider(settings.GOOGLE)

		# Authenticate token and get user's info from external provider
		external_user = await provider.get_user(
			auth_token=ExternalAuthToken(code=code)
		)
        
		user = UserCreate(
            full_name=external_user.username,
            email=external_user.email,
            password=''.join(random.choice(string.printable) for i in range(10)),
            is_active=1
        )

		# Get or create the internal user
		internal_user = cruduser.get_user_by_email(SessionLocal(), external_user.email)

		if internal_user is None:
			internal_user = cruduser.create_user(SessionLocal(), user)

		internal_auth_token = security.create_access_token(internal_user.id)

		# Redirect the user to the home page
		redirect_url = f"{settings.FRONTEND_URL}?authToken={internal_auth_token}"
		response = RedirectResponse(url=redirect_url)

		# Delete state cookie. No longer required
		response.delete_cookie(key="state")

		return response


@app.get("/azure-login-callback/")
async def azure_login_callback(
	request: Request,
	_ = Depends(csrf_token_redirect_cookie_scheme)
):
	""" Callback triggered when the user logs in to Azure's pop-up.

		Receives an authentication_token from Azure which then
		exchanges for an access_token. The latter is used to
		gain user information from Azure's userinfo_endpoint.

		Args:
			request: The incoming request as redirected by Azure
	"""
	async with exception_handling():
		code = request.query_params.get("code")

		if not code:
			raise AuthorizationException("Missing external authentication token")

		provider = await auth_providers.get_auth_provider(config.AZURE)

		# Authenticate token and get user's info from external provider
		external_user = await provider.get_user(
			auth_token=ExternalAuthToken(code=code)
		)

		print(external_user)

		user = UserCreate(
            full_name=external_user.username,
            email=external_user.email,
            password=''.join(random.choice(string.printable) for i in range(10)),
            is_active=1
        )

		# Get or create the internal user
		internal_user = cruduser.get_user_by_email(SessionLocal(), external_user.email)

		if internal_user is None:
			internal_user = cruduser.create_user(SessionLocal(), user)

		internal_auth_token = security.create_access_token(internal_user.id)

		# Redirect the user to the home page
		redirect_url = f"{config.FRONTEND_URL}?authToken={internal_auth_token}"
		response = RedirectResponse(url=redirect_url)

		# Delete state cookie. No longer required
		response.delete_cookie(key="state")

		return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
