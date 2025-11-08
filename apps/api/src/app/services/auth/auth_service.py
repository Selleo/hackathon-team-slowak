from fastapi import HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.jwt.password import hash_password, verify_password
from src.app.jwt.tokens import create_access_token, get_token_expiry
from src.app.jwt.blacklist import TokenBlacklist
from src.app.repositories.user.user_repository import UserRepository
from src.app.schemas.auth_schemas import UserRegister, UserLogin, UserResponse
from src.db.engine import DatabaseSessionManager

from uuid import UUID


class AuthService:
    """Service for authentication operations."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_blacklist: TokenBlacklist,
    ):
        self.user_repository = user_repository
        self.token_blacklist = token_blacklist

    async def register_user(self, user_data: UserRegister) -> UserResponse:
        """Register a new user."""
        exists, reason = await self.user_repository.user_exists(
            str(user_data.email), user_data.username
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=reason
            )

        hashed_password = hash_password(user_data.password)
        user = await self.user_repository.create(
            email=str(user_data.email),
            username=user_data.username,
            password_hash=hashed_password,
        )

        return UserResponse(**user.__dict__)

    async def authenticate_user(
        self, response: Response, credentials: UserLogin
    ) -> str:
        user = await self.user_repository.get_by_email(
            str(credentials.email)
        )

        if not user or not verify_password(
            credentials.password, str(user.passwordHash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": str(user.id)})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="none",
            secure=True,
        )

        return access_token

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserResponse(**user.__dict__)

    async def logout_user(self, response: Response, token: str) -> None:
        expiry_seconds = get_token_expiry(token)

        if expiry_seconds is None or expiry_seconds <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        response.delete_cookie("access_token")

        await self.token_blacklist.blacklist_token(token, expiry_seconds)
