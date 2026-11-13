"""Central configuration, loaded from .env at the project root."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    ollama_host: str = "http://127.0.0.1:11434"
    chat_model: str = "nemotron-3-nano"
    embed_model: str = "nomic-embed-text"
    ollama_think: bool = False
    llm_temperature: float = 0.2
    llm_timeout_seconds: int = 300

    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 480

    demo_username: str = "demo"
    demo_password: str = "PeoplesGuide2026!"

    rag_top_k: int = 8
    api_port: int = 8000

    db_path: Path = DATA_DIR / "app.db"
    sources_dir: Path = DATA_DIR / "sources"
    index_dir: Path = DATA_DIR / "index"
    trusted_sources_file: Path = DATA_DIR / "trusted_sources.json"
    frontend_dist: Path = ROOT_DIR / "frontend" / "dist"


settings = Settings()
