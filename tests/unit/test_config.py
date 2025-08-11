"""Unit tests for configuration management."""

from src.echoflow.config.settings import CacheConfig, ProcessingConfig, Settings


class TestSettings:
    """Test Settings configuration."""

    def test_default_settings(self):
        """Test default settings creation."""
        settings = Settings()

        assert settings.app_name == "EchoFlow"
        assert settings.version == "0.1.0"
        assert settings.debug is False
        assert settings.server.host == "localhost"
        assert settings.server.port == 3000

    def test_environment_override(self, monkeypatch):
        """Test environment variable overrides."""
        # Set environment variables
        monkeypatch.setenv("ECHOFLOW_SERVER__LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ECHOFLOW_PROCESSING__TEMP_DIR", "/custom/temp")
        monkeypatch.setenv("ECHOFLOW_CACHE__ENABLED", "false")

        settings = Settings()

        assert settings.server.log_level == "DEBUG"
        assert str(settings.processing.temp_dir) == "/custom/temp"
        assert settings.cache.enabled is False

    def test_processing_config_validation(self):
        """Test processing configuration validation."""
        config = ProcessingConfig(max_file_size=1024, max_batch_size=10, timeout_seconds=60)

        assert config.max_file_size == 1024
        assert config.max_batch_size == 10
        assert config.timeout_seconds == 60

    def test_cache_config_validation(self):
        """Test cache configuration validation."""
        config = CacheConfig(enabled=True, ttl_seconds=3600, max_size=1000)

        assert config.enabled is True
        assert config.ttl_seconds == 3600
        assert config.max_size == 1000
