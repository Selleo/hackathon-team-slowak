from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, status
from fastapi.params import Depends

from src.app.core.container import Container
from src.app.jwt.oauth2 import get_access_token
from src.app.jwt.tokens import decode_access_token
from src.app.jwt.blacklist import TokenBlacklist
from src.app.schemas.auth_schemas import UserResponse
from src.app.services.auth.auth_service import AuthService


@inject
async def get_current_user(
    token: Annotated[str, Depends(get_access_token)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    token_blacklist: TokenBlacklist = Depends(Provide[Container.token_blacklist])
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if await token_blacklist.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: UUID = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user = await auth_service.get_user_by_id(user_id)
        return user
    except HTTPException:
        raise credentials_exception
