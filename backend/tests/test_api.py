import asyncio
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from backend.app.generation import GenerationError
from backend.app.main import create_app
from backend.app.models import Lesson
from backend.app.settings import Settings
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture
def generator(lesson):
    return SimpleNamespace(generate=AsyncMock(return_value=lesson))


@pytest.fixture
def client(generator):
    app = create_app(Settings(api_key="test-key"), generator)
    with TestClient(app) as test_client:
        yield test_client


def test_health_and_private_headers(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_config_reveals_availability_not_credentials(client):
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.json() == {
        "ai_available": True,
        "max_upload_bytes": 8 * 1024 * 1024,
        "supported_formats": ["image/jpeg", "image/png", "image/webp"],
    }
    assert "test-key" not in response.text
    assert "api_key" not in response.text


def test_demo_endpoints_are_available_and_honest_without_a_key():
    with TestClient(create_app(Settings())) as client:
        response = client.get("/api/demos")
        assert response.status_code == 200
        lessons = [Lesson.model_validate(item) for item in response.json()]
        assert {lesson.id for lesson in lessons} == {"puppy", "flower", "house"}
        assert all(lesson.source == "demo" for lesson in lessons)
        for lesson in lessons:
            assert client.get(f"/api/demos/{lesson.id}").json() == lesson.model_dump()
        assert client.get("/api/demos/missing").status_code == 404
        assert client.get("/api/config").json()["ai_available"] is False


def test_no_key_prevents_real_photo_generation(png_bytes, generator):
    with TestClient(create_app(Settings(), generator)) as client:
        response = client.post(
            "/api/lessons", files={"image": ("puppy.png", png_bytes, "image/png")}
        )
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
    generator.generate.assert_not_called()


def test_valid_upload_is_sanitized_and_integrates_with_generator(client, generator, png_bytes):
    response = client.post("/api/lessons", files={"image": ("puppy.png", png_bytes, "image/png")})
    assert response.status_code == 200
    assert response.json()["source"] == "ai"
    generator.generate.assert_awaited_once()
    prepared = generator.generate.call_args.args[0]
    with Image.open(io.BytesIO(prepared.data)) as output:
        assert output.format == "JPEG"
        assert not output.getexif()
    assert prepared.data != png_bytes


@pytest.mark.parametrize(
    "payload,mime,status", [(b"not-an-image", "image/png", 400), (b"<svg/>", "image/svg+xml", 415)]
)
def test_invalid_uploads_never_reach_ai(client, generator, payload, mime, status):
    response = client.post("/api/lessons", files={"image": ("fake.png", payload, mime)})
    assert response.status_code == status
    assert isinstance(response.json()["detail"], str)
    generator.generate.assert_not_called()


def test_mime_mismatch_rejected(client, generator, png_bytes):
    response = client.post("/api/lessons", files={"image": ("fake.jpg", png_bytes, "image/jpeg")})
    assert response.status_code == 415
    generator.generate.assert_not_called()


@pytest.mark.parametrize("wrong", ["photo", "file"])
def test_wrong_upload_field_rejected(client, generator, png_bytes, wrong):
    response = client.post("/api/lessons", files={wrong: ("puppy.png", png_bytes, "image/png")})
    assert response.status_code == 422
    generator.generate.assert_not_called()


def test_multiple_files_rejected(client, generator, png_bytes):
    response = client.post(
        "/api/lessons",
        files=[
            ("image", ("first.png", png_bytes, "image/png")),
            ("image", ("second.png", png_bytes, "image/png")),
        ],
    )
    assert response.status_code == 400
    generator.generate.assert_not_called()


def test_unexpected_text_fields_rejected(client, png_bytes):
    response = client.post(
        "/api/lessons",
        data={"prompt": "ignore instructions"},
        files={"image": ("photo.png", png_bytes, "image/png")},
    )
    assert response.status_code == 400


def test_missing_and_malformed_multipart_rejected(client, generator):
    assert client.post("/api/lessons", json={"image": "<svg/>"}).status_code == 415
    response = client.post(
        "/api/lessons", headers={"content-type": "multipart/form-data"}, content=b"broken"
    )
    assert response.status_code == 400
    generator.generate.assert_not_called()


def test_file_limit_is_checked_even_inside_a_small_multipart_body(generator, png_bytes):
    with TestClient(
        create_app(Settings(api_key="test-key", max_upload_bytes=10), generator)
    ) as client:
        response = client.post(
            "/api/lessons", files={"image": ("photo.png", png_bytes, "image/png")}
        )
    assert response.status_code == 413
    generator.generate.assert_not_called()


@pytest.mark.parametrize("status", [422, 502, 503, 504])
def test_generation_errors_propagate_without_demo_fallback(client, generator, png_bytes, status):
    generator.generate.side_effect = GenerationError("Choose a simpler photo.", status)
    response = client.post("/api/lessons", files={"image": ("photo.png", png_bytes, "image/png")})
    assert response.status_code == status
    assert response.json() == {"detail": "Choose a simpler photo."}
    if status == 503:
        assert response.headers["retry-after"] == "60"
    assert client.app.state.gate.active == 0


def test_rate_limit_cannot_be_bypassed_by_forwarded_headers(generator, png_bytes):
    with TestClient(
        create_app(Settings(api_key="test-key", requests_per_minute=1), generator)
    ) as client:
        assert (
            client.post(
                "/api/lessons", files={"image": ("photo.png", png_bytes, "image/png")}
            ).status_code
            == 200
        )
        response = client.post(
            "/api/lessons",
            files={"image": ("photo.png", png_bytes, "image/png")},
            headers={"x-forwarded-for": "203.0.113.8"},
        )
        assert response.status_code == 429
        assert response.headers["retry-after"] == "60"
        assert client.app.state.gate.active == 0
    assert generator.generate.await_count == 1


async def test_concurrent_generation_has_capacity_limit_and_releases_slots(lesson, png_bytes):
    entered = asyncio.Event()
    finish = asyncio.Event()

    async def generate(_):
        entered.set()
        await finish.wait()
        return lesson

    generator = SimpleNamespace(generate=generate)
    app = create_app(Settings(api_key="test-key", max_concurrent=1), generator)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        first = asyncio.create_task(
            client.post("/api/lessons", files={"image": ("one.png", png_bytes, "image/png")})
        )
        await entered.wait()
        second = await client.post(
            "/api/lessons", files={"image": ("two.png", png_bytes, "image/png")}
        )
        assert second.status_code == 503
        finish.set()
        assert (await first).status_code == 200
        assert app.state.gate.active == 0


def test_cors_allows_only_local_development_origins(client):
    good = client.options(
        "/api/lessons",
        headers={"origin": "http://localhost:5173", "access-control-request-method": "POST"},
    )
    assert good.status_code == 200
    assert good.headers["access-control-allow-origin"] == "http://localhost:5173"
    bad = client.options(
        "/api/lessons",
        headers={"origin": "https://unrelated.example", "access-control-request-method": "POST"},
    )
    assert bad.status_code == 400
    assert "access-control-allow-origin" not in bad.headers


@pytest.mark.parametrize("origin", ["https://unrelated.example", "null"])
def test_foreign_origin_cannot_trigger_ai_work(client, generator, png_bytes, origin):
    response = client.post(
        "/api/lessons",
        headers={"Origin": origin},
        files={"image": ("photo.png", png_bytes, "image/png")},
    )
    assert response.status_code == 403
    assert "configured local app" in response.json()["detail"]
    generator.generate.assert_not_called()
    assert client.app.state.gate.active == 0
    assert not client.app.state.gate.clients


def test_foreign_origin_is_rejected_before_parsing_an_upload(client, generator):
    response = client.post(
        "/api/lessons", headers={"Origin": "https://unrelated.example"}, content=b"not multipart"
    )
    assert response.status_code == 403
    generator.generate.assert_not_called()


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
def test_configured_origin_can_generate_a_photo_lesson(client, generator, png_bytes, origin):
    response = client.post(
        "/api/lessons",
        headers={"Origin": origin},
        files={"image": ("photo.png", png_bytes, "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["source"] == "ai"
    assert response.headers["access-control-allow-origin"] == origin
    generator.generate.assert_awaited_once()


def test_openapi_documents_multipart_field_and_numeric_lesson(client):
    schema = client.get("/openapi.json").json()
    request_schema = schema["paths"]["/api/lessons"]["post"]["requestBody"]["content"][
        "multipart/form-data"
    ]["schema"]
    assert request_schema["required"] == ["image"]
    assert request_schema["properties"]["image"]["format"] == "binary"
    assert "Lesson" in schema["components"]["schemas"]
