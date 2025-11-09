from typing import Annotated, List
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.app.core.container import Container
from src.app.jwt.jwt_strategy import get_current_user
from src.app.schemas.auth_schemas import UserResponse
from src.app.schemas.draft_schemas import (
    CreateDraftRequestBody,
    DraftResponseBody,
)
from src.app.services.draft.draft_service import DraftService

draft_router = APIRouter(prefix="/api/v1/draft")


@draft_router.get("/all", response_model=List[DraftResponseBody])
@inject
async def get_all_drafts(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    draft_service: Annotated[DraftService, Depends(Provide(Container.draft_service))],
):
    return await draft_service.get_all_drafts(current_user)


@draft_router.post("", response_model=DraftResponseBody)
@inject
async def create_draft(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    draft_service: Annotated[DraftService, Depends(Provide(Container.draft_service))],
    data: CreateDraftRequestBody,
):
    return await draft_service.create_draft(current_user, data)


@draft_router.get("/{draft_id}", response_model=DraftResponseBody)
@inject
async def get_draft(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    draft_id: UUID,
    draft_service: Annotated[DraftService, Depends(Provide(Container.draft_service))],
):
    return await draft_service.get_draft(current_user, draft_id)


@draft_router.delete("/{draft_id}")
@inject
async def delete_draft(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    draft_id: UUID,
    draft_service: Annotated[DraftService, Depends(Provide(Container.draft_service))],
):
    return await draft_service.delete_draft(current_user, draft_id)
