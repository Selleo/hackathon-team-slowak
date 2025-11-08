from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.draft_schemas import CreateDraft
from src.db.models import Draft


class DraftRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_drafts(self, user_id: UUID):
        result = (
            (await self.db.execute(select(Draft).where(Draft.userId == user_id)))
            .scalars()
            .all()
        )
        return result

    async def create_draft(self, data: CreateDraft):
        draft = Draft(**data.__dict__)

        self.db.add(draft)
        await self.db.commit()
        await self.db.refresh(draft)

        return draft

    async def get_draft(self, draft_id: UUID):
        return await self.db.get(Draft, draft_id)

    async def delete_draft(self, draft_id: UUID):
        await self.db.execute(delete(Draft).where(Draft.id == draft_id))
        await self.db.commit()
