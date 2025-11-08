import redis.asyncio as redis

class TokenBlacklist:
    """Redis-based token blacklist for logout functionality."""

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def blacklist_token(self, token: str, expiry_seconds: int):
        """Add a token to the blacklist with expiry."""
        await self.redis_client.setex(f"blacklist:{token}", expiry_seconds, "1")

    async def is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted."""
        result = await self.redis_client.exists(f"blacklist:{token}")

        return result > 0
