from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.nodes import router as node_router
from app.api.routes.tasks import router as task_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.ws.node_ws import lifespan_context, router as node_ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    async with lifespan_context():
        yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(node_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(node_ws_router)


@app.get("/")
def health_check():
    return {"message": "Agent Resource Server is running."}
