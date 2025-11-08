from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from dotenv import load_dotenv

from src.app.jwt.blacklist import TokenBlacklist
from src.app.repositories.draft.draft_repository import DraftRepository
from src.app.repositories.user.user_repository import UserRepository
from src.app.services.auth.auth_service import AuthService
from src.app.services.draft.draft_service import DraftService
from src.db.engine import get_db_session
import redis.asyncio as redis
import os

load_dotenv()


class Container(DeclarativeContainer):
    config = providers.Configuration()

    redis_client = providers.Resource(
        redis.Redis.from_url,
        os.getenv("REDIS_URL", "redis://localhost:6379"),
    )

    db_session = providers.Resource(get_db_session)

    token_blacklist = providers.Factory(TokenBlacklist, redis_client)

    user_repository = providers.Factory(UserRepository, db_session)
    auth_service = providers.Factory(AuthService, user_repository, token_blacklist)

    draft_repository = providers.Factory(DraftRepository, db_session)
    draft_service = providers.Factory(DraftService, draft_repository)



