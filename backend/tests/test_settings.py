import pytest
from backend.app.settings import Settings


def test_key_is_never_printed_in_settings_representation():
    assert "private-secret" not in repr(Settings(api_key="private-secret"))


@pytest.mark.parametrize("key", [None, "", "   "])
def test_empty_key_means_demo_mode(key):
    assert Settings(api_key=key).ai_available is False


def test_environment_values_and_model_names_are_configurable(monkeypatch):
    monkeypatch.setattr("backend.app.settings.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_VISION_MODEL", "vision-test")
    monkeypatch.setenv("OPENAI_DRAWING_MODEL", "drawing-test")
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "4096")
    monkeypatch.setenv("AI_REQUESTS_PER_MINUTE", "2")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173, http://127.0.0.1:5173")
    settings = Settings.from_environment()
    assert settings.ai_available is True
    assert settings.vision_model == "vision-test"
    assert settings.drawing_model == "drawing-test"
    assert settings.max_upload_bytes == 4096
    assert settings.requests_per_minute == 2
    assert settings.cors_origins == ("http://localhost:5173", "http://127.0.0.1:5173")


@pytest.mark.parametrize("value", ["invalid", "-1", "0", "61"])
def test_invalid_limits_fail_at_startup_without_echoing_values(monkeypatch, value):
    monkeypatch.setattr("backend.app.settings.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("AI_REQUESTS_PER_MINUTE", value)
    with pytest.raises(ValueError, match="AI_REQUESTS_PER_MINUTE"):
        Settings.from_environment()
