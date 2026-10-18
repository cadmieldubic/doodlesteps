"""Environment-only server configuration; credentials never enter API responses."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


def _integer(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


@dataclass(frozen=True)
class Settings:
    api_key: str | None = field(default=None, repr=False)
    vision_model: str = "gpt-5.4"
    drawing_model: str = "gpt-5.4"
    request_timeout_seconds: int = 60
    max_output_tokens: int = 12000
    max_upload_bytes: int = 8 * 1024 * 1024
    max_image_pixels: int = 24_000_000
    max_image_dimension: int = 1280
    requests_per_minute: int = 6
    max_concurrent: int = 2
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    @property
    def ai_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    @classmethod
    def from_environment(cls) -> "Settings":
        workspace = Path(__file__).resolve().parents[2]
        load_dotenv(workspace / ".env", override=False)
        load_dotenv(workspace / "backend" / ".env", override=False)
        api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
        return cls(
            api_key=api_key,
            vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-5.4"),
            drawing_model=os.getenv("OPENAI_DRAWING_MODEL", "gpt-5.4"),
            request_timeout_seconds=_integer("OPENAI_TIMEOUT_SECONDS", 60, 1, 180),
            max_output_tokens=_integer("OPENAI_MAX_OUTPUT_TOKENS", 12000, 2000, 32000),
            max_upload_bytes=_integer("MAX_UPLOAD_BYTES", 8 * 1024 * 1024, 1024, 20 * 1024 * 1024),
            max_image_pixels=_integer("MAX_IMAGE_PIXELS", 24_000_000, 10000, 50_000_000),
            max_image_dimension=_integer("MAX_IMAGE_DIMENSION", 1280, 128, 2048),
            requests_per_minute=_integer("AI_REQUESTS_PER_MINUTE", 6, 1, 60),
            max_concurrent=_integer("AI_MAX_CONCURRENT", 2, 1, 8),
            cors_origins=tuple(
                origin.strip()
                for origin in os.getenv(
                    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
                ).split(",")
                if origin.strip()
            ),
        )
