from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from src.app.core.ai.ai_schema import Message
from src.app.core.container import Container
from src.app.jwt.jwt_strategy import get_current_user
from src.app.schemas.auth_schemas import UserResponse
from src.app.services.ai.ai_service import AiService

ai_router = APIRouter(prefix="/api/v1/ai")


@ai_router.post("/chat/{draft_id}")
@inject
async def chat(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    draft_id: UUID,
    message: Message,
    ai_service: Annotated[AiService, Depends(Provide(Container.ai_service))],
):
    return StreamingResponse(
        ai_service.chat(current_user, message.message, draft_id),
        media_type="text/plain; charset=utf-8",
        headers={
            "X-Vercel-AI-Data-Stream": "v1",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@ai_router.get("/{draft_id}")
@inject
async def chat(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    draft_id: UUID,
    ai_service: Annotated[AiService, Depends(Provide(Container.ai_service))],
):
    return await ai_service.get_draft_messages(current_user, draft_id)
