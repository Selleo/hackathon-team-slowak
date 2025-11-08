from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, status, Response
from fastapi.params import Depends

from src.app.core.container import Container
from src.app.jwt.jwt_strategy import get_current_user
from src.app.jwt.oauth2 import get_access_token
from src.app.schemas.auth_schemas import UserRegister, UserLogin, Token, UserResponse
from src.app.services.auth.auth_service import AuthService
from src.db.models.user import User

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@auth_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    return await auth_service.register_user(user_data)


@auth_router.post("/login", response_model=Token)
@inject
async def login(
    response: Response,
    credentials: UserLogin,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    access_token = await auth_service.authenticate_user(response, credentials)
    return {"accessToken": access_token, "tokenType": "bearer"}


@auth_router.post("/logout")
@inject
async def logout(
    response: Response,
    token: Annotated[str, Depends(get_access_token)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    await auth_service.logout_user(response, token)
    return {"message": "Successfully logged out"}


@auth_router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
