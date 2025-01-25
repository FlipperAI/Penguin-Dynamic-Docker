from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users
from app.router import ( submissions_router )
from fastapi.middleware.cors import CORSMiddleware


from httpx_oauth.clients.github import GitHubOAuth2

github_oauth_client = GitHubOAuth2("Ov23liPzwZAfbD3KVu1n", "dc9d3f4d7a90155223dd338de4c2f90034c9a3fc", name='github')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    submissions_router,
    prefix="/submissions",
    tags=["submissions"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        github_oauth_client,
        auth_backend,
        "SECRET",
        associate_by_email=True,
        is_verified_by_default=True,
    ),
    prefix="/auth/github",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_associate_router(github_oauth_client, UserRead, "SECRET"),
    prefix="/auth/associate/github",
    tags=["auth"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

