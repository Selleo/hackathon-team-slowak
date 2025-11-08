from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_access_token(request: Request) -> str:
    """Extract access token from cookie or Authorization header."""
    token = request.cookies.get("access_token")
    if token:
        return token

    token = await oauth2_scheme(request)
    if token:
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
