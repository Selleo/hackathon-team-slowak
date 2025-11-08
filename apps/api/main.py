import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.controllers.ai.ai_controller import ai_router
from src.app.controllers.auth.auth_controller import auth_router
from src.app.controllers.draft.draft_controller import draft_router
from src.app.core.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    with open("api-schema.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)
    yield


app = FastAPI(lifespan=lifespan)

container = Container()
container.wire(
    modules=[
        "src.app.controllers.auth.auth_controller",
        "src.app.controllers.draft.draft_controller",
        "src.app.controllers.ai.ai_controller",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(draft_router)

app.include_router(ai_router)
