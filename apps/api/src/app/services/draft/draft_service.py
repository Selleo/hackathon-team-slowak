from uuid import UUID

from fastapi import HTTPException

from src.app.repositories.draft.draft_repository import DraftRepository
from src.app.schemas.auth_schemas import UserResponse
from src.app.schemas.draft_schemas import (
    CreateDraftRequestBody,
    CreateDraft,
    DraftResponseBody,
)


class DraftService:
    def __init__(self, draft_repository: DraftRepository):
        self.draft_repository = draft_repository

    async def get_all_drafts(self, current_user: UserResponse):
        drafts = await self.draft_repository.get_all_drafts(current_user.id)

        if len(drafts) == 0:
            raise HTTPException(status_code=404, detail="NOT_FOUND")

        return [DraftResponseBody(**draft.__dict__) for draft in drafts]

    async def get_draft(self, current_user: UserResponse, draft_id: UUID):
        draft = await self.draft_repository.get_draft(draft_id)

        if not draft or draft.userId != current_user.id:
            raise HTTPException(status_code=404, detail="NOT_FOUND")

        return DraftResponseBody(**draft.__dict__)

    async def create_draft(
        self, current_user: UserResponse, data: CreateDraftRequestBody
    ):
        draft = await self.draft_repository.create_draft(
            data=CreateDraft(userId=current_user.id, draftName=data.draftName)
        )

        return DraftResponseBody(**draft.__dict__)

    async def delete_draft(self, current_user: UserResponse, draft_id: UUID):
        draft = await self.draft_repository.get_draft(draft_id)

        if not draft or draft.userId != current_user.id:
            raise HTTPException(status_code=404, detail="NOT_FOUND")

        await self.draft_repository.delete_draft(
            draft_id,
        )

        return {"message": "Draft deleted successfully"}
