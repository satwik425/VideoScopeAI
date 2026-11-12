from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:5173"

    database_url: str = "sqlite:///./vidscope.db"
    storage_root: str = "./storage"
    max_upload_mb: int = 500
    allowed_extensions: tuple[str, ...] = (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v")

    asr_model_size: str = "base"
    asr_device: str = "auto"
    asr_compute_type: str = "auto"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    retrieval_top_k: int = 5
    min_similarity: float = 0.25

    # Visual pipeline (Phase 6)
    clip_model: str = "openai/clip-vit-base-patch32"
    frame_sample_interval: float = 2.0      # seconds between candidate frames
    frame_change_threshold: float = 6.0     # mean abs pixel diff (0-255) to keep a frame
    frame_max_gap: float = 30.0             # always keep a frame at least this often
    frame_max_count: int = 400
    visual_top_k: int = 4
    visual_min_similarity: float = 0.20     # CLIP text-image cosine, general questions
    visual_intent_min_similarity: float = 0.15  # used when the question asks about visuals

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_root).resolve()


settings = Settings()
