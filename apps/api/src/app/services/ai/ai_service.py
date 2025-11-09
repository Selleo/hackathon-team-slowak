import asyncio
import os
import uuid

import httpx
from fastapi import HTTPException
from uuid import UUID

import psycopg
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import Command


from src.app.core.ai.ai_agent import (
    data_curator,
    repeat_curator,
    objective_architect,
    evaluator_oa,
    curriculum_designer,
    evaluator_cd,
    lesson_author,
)
from src.app.core.ai.ai_schema import MessagesState, AuthData
from src.app.repositories.draft.draft_repository import DraftRepository
from src.app.schemas.auth_schemas import UserResponse

load_dotenv()


class AiService:
    _setup_lock = asyncio.Lock()

    def __init__(self, draft_repository: DraftRepository):
        url = os.getenv("DATABASE_URL")
        self.database_url = url.replace("postgresql+psycopg://", "postgresql://")
        self.draft_repository = draft_repository

        self.graph = None
        self.conn = None

    async def setup_graph(self):
        async with AiService._setup_lock:
            if self.graph is not None:
                return
            conn = await psycopg.AsyncConnection.connect(
                self.database_url, autocommit=True
            )
            checkpointer = AsyncPostgresSaver(conn=conn)
            await checkpointer.setup()

            builder = StateGraph(MessagesState)

            builder.add_node("data_curator", data_curator)
            builder.add_node("repeat_curator", repeat_curator)
            builder.add_node("objective_architect", objective_architect)
            builder.add_node("evaluator_oa", evaluator_oa)
            builder.add_node("curriculum_designer", curriculum_designer)
            builder.add_node("evaluator_cd", evaluator_cd)
            # builder.add_node("evaluator_la", evaluator_la)
            builder.add_node("lesson_author", lesson_author)

            builder.add_edge(START, "data_curator")
            builder.add_edge("repeat_curator", "data_curator")

            self.conn = conn

            self.graph = builder.compile(checkpointer=checkpointer)

    async def chat(self, current_user: UserResponse, message: str, draft_id: UUID):
        if not self.graph:
            await self.setup_graph()

        draft = await self.draft_repository.get_draft(draft_id)

        if draft.userId != current_user.id:
            raise HTTPException(status_code=404, detail="DRAFT_NOT_FOUND")

        if draft.closedAt is not None:
            raise HTTPException(status_code=400, detail="DRAFT_ALREADY_COMPLETED")

        config = {"configurable": {"thread_id": draft_id.hex}}

        last_state = await self.graph.aget_state(config)

        input_state = {"messages": [HumanMessage(content=message)]}

        if last_state and last_state.values:
            has_interrupt = "__interrupt__" in last_state.values

            if has_interrupt:
                input_state = Command(resume=message)

        async for event in self.graph.astream(input_state, config):
            if "data_curator" in event:
                yield f'0:"{event.get("data_curator").get("messages")[-1].content}"\n'

    async def get_draft_messages(self, current_user: UserResponse, draft_id: UUID):
        if not self.graph:
            await self.setup_graph()

        draft = await self.draft_repository.get_draft(draft_id)

        if not draft or draft.userId != current_user.id:
            return []

        config = {"configurable": {"thread_id": draft_id.hex}}

        last_state = await self.graph.aget_state(config)

        return last_state.values.get("messages")

    async def get_course_schema(self, current_user: UserResponse, draft_id: UUID):
        if not self.graph:
            await self.setup_graph()

        draft = await self.draft_repository.get_draft(draft_id)

        if not draft or draft.userId != current_user.id:
            raise HTTPException(status_code=404, detail="NOT_FOUND")

        config = {"configurable": {"thread_id": draft_id.hex}}

        last_state = await self.graph.aget_state(config)

        return last_state.values.get("course")

    async def export_to_lms(
        self, current_user: UserResponse, auth_data: AuthData, draft_id: UUID
    ):
        if not self.graph:
            await self.setup_graph()

        draft = await self.draft_repository.get_draft(draft_id)

        if not draft or draft.userId != current_user.id:
            raise HTTPException(status_code=404, detail="NOT_FOUND")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="http://localhost:3000/api/auth/login",
                data={"email": auth_data.email, "password": auth_data.password},
            )

        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        access_token = response.cookies.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}

        config = {"configurable": {"thread_id": draft_id.hex}}

        last_state = await self.graph.aget_state(config)

        course = last_state.values.get("course")

        if not course:
            raise HTTPException(status_code=400, detail="NO_COURSE_SCHEMA_CREATED")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="http://localhost:3000/api/category",
                data={"title": (draft.draftName + uuid.uuid4().hex)[:100]},
                headers=headers,
            )

            if response.status_code != 201:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )

            category = response.json().get("data").get("id")

            response = await client.post(
                url="http://localhost:3000/api/course",
                data={
                    "title": course.get("title", "")[:100],
                    "description": course.get("description"),
                    "categoryId": category,
                },
                headers=headers,
            )

            if response.status_code != 201:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )

            course_id = response.json().get("data").get("id")

            for chapter in course.get("chapters"):
                response = await client.post(
                    url="http://localhost:3000/api/chapter/beta-create-chapter",
                    data={
                        "courseId": course_id,
                        "title": chapter.get("title", "")[:100],
                    },
                    headers=headers,
                )

                if response.status_code != 201:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                chapter_id = response.json().get("data").get("id")

                for lesson in chapter.get("lessons"):
                    if lesson.get("type") == "ai_mentor":
                        response = await client.post(
                            url="http://localhost:3000/api/lesson/beta-create-lesson/ai",
                            data={
                                "chapterId": chapter_id,
                                "title": lesson.get("title", "")[:100],
                                "aiMentorInstructions": lesson.get(
                                    "ai_mentor_instructions"
                                ),
                                "completionConditions": lesson.get(
                                    "ai_completion_conditions"
                                ),
                                "type": lesson.get("mentor_type"),
                            },
                            headers=headers,
                        )
                    else:
                        response = await client.post(
                            url="http://localhost:3000/api/lesson/beta-create-lesson",
                            data={
                                "chapterId": chapter_id,
                                "title": lesson.get("title", "")[:100],
                                "description": lesson.get("content"),
                                "type": lesson.get("type"),
                            },
                            headers=headers,
                        )

                    if response.status_code not in [200, 201]:
                        raise HTTPException(
                            status_code=response.status_code, detail=response.text
                        )

        return {"message": "Exported course"}
