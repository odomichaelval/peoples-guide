"""People's Guide API.

Run from the project root:
    source .venv/bin/activate
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
API docs: http://<spark>:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend import auth, db
from backend.app.routes_auth import router as auth_router
from backend.app.routes_guide import router as guide_router
from backend.config import settings
from backend.rag.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    if not db.get_user(settings.demo_username):
        db.create_user(settings.demo_username, auth.hash_password(settings.demo_password), "Demo User")
        print(f"[startup] created demo user '{settings.demo_username}'")
    if not store.load():
        print("[startup] no index found - building from data/sources ...")
        print(f"[startup] index: {await store.build()}")
    else:
        print(f"[startup] loaded index: {len(store.chunks)} chunks, embedded={store.vectors is not None}")
    yield


app = FastAPI(title="People's Guide API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(guide_router)

# Serve the built React app (npm run build) from the same port in "production" mode.
if settings.frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=settings.frontend_dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = settings.frontend_dist / path
        if path and f.is_file():
            return FileResponse(f)
        return FileResponse(settings.frontend_dist / "index.html")
