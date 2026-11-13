"""People's Guide API + website, all on one port.

Run from the project root:  bash scripts/start.sh
  http://localhost:8000/site/   -> teammate's pages (site/ folder)
  http://localhost:8000/        -> React agent dashboard (frontend/dist)
  http://localhost:8000/api/... -> API      http://localhost:8000/docs -> Swagger
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend import auth, db
from backend.app.routes_auth import router as auth_router
from backend.app.routes_guide import router as guide_router
from backend.config import ROOT_DIR, settings
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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 1) API routes (must come first)
app.include_router(auth_router)
app.include_router(guide_router)

# 2) Teammate's static website: site/index.html, login.html, register.html, ...
SITE_DIR = ROOT_DIR / "site"
if SITE_DIR.exists():
    @app.get("/site", include_in_schema=False)
    def site_redirect():
        return RedirectResponse("/site/")

    app.mount("/site", StaticFiles(directory=SITE_DIR, html=True), name="site")

# 3) React agent dashboard (built with: cd frontend && npm run build)
if settings.frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=settings.frontend_dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = settings.frontend_dist / path
        if path and f.is_file():
            return FileResponse(f)
        return FileResponse(settings.frontend_dist / "index.html")