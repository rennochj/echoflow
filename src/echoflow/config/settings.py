"""Configuration management for EchoFlow."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class ServerConfig(BaseModel):
    """Server configuration settings."""

    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=3000, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    enable_cors: bool = Field(default=True, description="Enable CORS")
    max_request_size: int = Field(default=52428800, description="Max request size (50MB)")


class ProcessingConfig(BaseModel):
    """Document processing configuration."""

    temp_dir: Path = Field(default=Path("/tmp/echoflow"), description="Temporary directory")
    max_file_size: int = Field(default=52428800, description="Maximum file size (50MB)")
    max_batch_size: int = Field(default=100, description="Maximum batch processing size")
    timeout_seconds: int = Field(default=300, description="Processing timeout (5 minutes)")
    supported_formats: list[str] = Field(
        default=["pdf", "docx", "pptx", "txt", "html", "md"], description="Supported file formats"
    )


class CacheConfig(BaseModel):
    """Caching configuration."""

    enabled: bool = Field(default=True, description="Enable caching")
    ttl_seconds: int = Field(default=3600, description="Cache TTL (1 hour)")
    max_size: int = Field(default=1000, description="Maximum cached items")
    cache_dir: Path = Field(default=Path(".cache"), description="Cache directory")


class AIModelConfig(BaseModel):
    """AI model configuration."""

    docling_model_path: Optional[str] = Field(default=None, description="Docling model path")
    enable_gpu: bool = Field(default=False, description="Enable GPU acceleration")
    model_cache_dir: Path = Field(
        default=Path(".cache/models"), description="Model cache directory"
    )
    download_timeout: int = Field(default=600, description="Model download timeout (10 minutes)")


class Settings(BaseSettings):
    """Main application settings."""

    # Application info
    app_name: str = Field(default="EchoFlow", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Component configurations
    server: ServerConfig = Field(default_factory=ServerConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    ai_models: AIModelConfig = Field(default_factory=AIModelConfig)

    model_config = ConfigDict(
        env_prefix="ECHOFLOW_",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    # Environment-based overrides
    @field_validator("processing", mode="before")
    @classmethod
    def override_processing_from_env(cls, v: dict) -> dict:
        """Override processing config from environment variables."""
        if isinstance(v, dict):
            # Override temp_dir from ECHOFLOW_TEMP_DIR
            if temp_dir := os.getenv("ECHOFLOW_TEMP_DIR"):
                v["temp_dir"] = temp_dir

            # Override max_file_size from ECHOFLOW_MAX_FILE_SIZE
            if max_size := os.getenv("ECHOFLOW_MAX_FILE_SIZE"):
                v["max_file_size"] = int(max_size)

        return v

    @field_validator("cache", mode="before")
    @classmethod
    def override_cache_from_env(cls, v: dict) -> dict:
        """Override cache config from environment variables."""
        if isinstance(v, dict):
            # Override enabled from ECHOFLOW_CACHE_ENABLED
            if cache_enabled := os.getenv("ECHOFLOW_CACHE_ENABLED"):
                v["enabled"] = cache_enabled.lower() in ("true", "1", "yes")

            # Override TTL from ECHOFLOW_CACHE_TTL
            if cache_ttl := os.getenv("ECHOFLOW_CACHE_TTL"):
                v["ttl_seconds"] = int(cache_ttl)

        return v

    @field_validator("server", mode="before")
    @classmethod
    def override_server_from_env(cls, v: dict) -> dict:
        """Override server config from environment variables."""
        if isinstance(v, dict):
            # Override log_level from ECHOFLOW_LOG_LEVEL
            if log_level := os.getenv("ECHOFLOW_LOG_LEVEL"):
                v["log_level"] = log_level.upper()

        return v


# Global settings instance
settings = Settings()
