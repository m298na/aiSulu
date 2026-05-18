from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
LOGS_DIR = APP_DIR / "logs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI.Sulu API"
    app_env: str = "development"
    api_v1_prefix: str = "/api"
    frontend_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    database_url: str = f"sqlite:///{(DATA_DIR / 'ai_sulu.db').as_posix()}"
    seed_faq_path: Path = DATA_DIR / "seed_faq.json"
    questions_log_path: Path = LOGS_DIR / "question_logs.jsonl"

    use_mock_services: bool = True
    fallback_message: str = (
        "Я не уверена, пожалуйста, обратитесь к сотруднику университета."
    )
    faq_match_threshold: float = 0.42

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_enabled: bool = False

    whisper_provider: str = "mock"
    elevenlabs_api_key: str = ""
    azure_tts_key: str = ""
    azure_tts_region: str = ""
    tts_provider: str = "mock"

    def get_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]

    def ensure_directories(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
