from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Job Intelligence Platform"
    environment: str = "development"

    # Falls back to a local SQLite file when no DATABASE_URL is provided, so the
    # app runs without Postgres/Docker for local development.
    database_url: str = "sqlite:///./job_intelligence.db"

    # LLM provider for resume parsing/tailoring assistance: "ollama" (free, local, default),
    # "groq" (free tier, cloud), "anthropic" (paid), or "none" (rule-based/template only).
    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"

    cors_origins: list[str] = ["http://localhost:3000"]

    resume_storage_dir: str = "./storage/resumes"

    scraper_seed_greenhouse: list[str] = ["stripe", "airbnb", "gitlab"]
    scraper_seed_lever: list[str] = ["netflix", "figma"]
    scraper_seed_ashby: list[str] = ["ramp", "notion"]
    scraper_seed_smartrecruiters: list[str] = ["Visa"]
    scraper_seed_workable: list[str] = []

    enable_scheduler: bool = True
    scheduler_interval_hours: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()
