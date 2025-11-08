from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateDraft(BaseModel):
    userId: UUID
    draftName: str


class CreateDraftRequestBody(BaseModel):
    draftName: str


class DraftResponseBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draftName: str
    userId: UUID
    id: UUID
    createdAt: datetime
    updatedAt: datetime
    closedAt: Optional[datetime]
