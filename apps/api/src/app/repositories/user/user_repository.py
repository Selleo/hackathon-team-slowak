from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User

from uuid import UUID


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(
        self, email: str
    ) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(
        self, user_id: UUID
    ) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(
        self, username: str
    ) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        username: str,
        password_hash: str,
    ) -> User:
        user = User(email=email, username=username, passwordHash=password_hash)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def user_exists(
        self, email: str, username: str
    ) -> tuple[bool, str | None]:

        result = await self.db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.email == email:
                return True, "Email already registered"
            else:
                return True, "Username already taken"

        return False, None
