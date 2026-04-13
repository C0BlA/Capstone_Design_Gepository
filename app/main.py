from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.nodes import router as node_router
from app.api.routes.tasks import router as task_router
from app.core.config import settings
from app.ws.node_ws import lifespan_context, router as node_ws_router
from app.ws.monitor_ws import router as monitor_ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with lifespan_context():
        yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(auth_router, prefix="/api")
app.include_router(node_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(node_ws_router)
app.include_router(monitor_ws_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def health_check():
    return FileResponse("static/monitor.html")