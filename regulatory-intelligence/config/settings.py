"""Configuration scaffold.

Keep all settings local and offline. Do not add API keys for cloud services.
"""

from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings for local development."""

    app_name: str = "Offline Regulatory Intelligence Platform"
    database_url: str = "sqlite:///./data/regulatory_intelligence.db"
    vector_index_path: str = "./data/vector_indexes/faiss"
    document_store_path: str = "./data/documents"
    local_model_path: str = "./models"
    enable_ollama: bool = False
    enable_llama_cpp: bool = False


settings = Settings()
