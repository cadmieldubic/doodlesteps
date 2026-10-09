import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from backend.app.generation import GenerationError, LessonGenerator
from backend.app.images import PreparedImage
from backend.app.models import Analysis, Lesson
from backend.app.settings import Settings
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)


def stub_client(*responses):
    return SimpleNamespace(
        responses=SimpleNamespace(
            parse=AsyncMock(
                side_effect=[SimpleNamespace(output_parsed=value) for value in responses]
            )
        ),
        close=AsyncMock(),
    )


@pytest.fixture
def prepared():
    return PreparedImage(b"sanitized-photo", 120, 80)


async def test_two_stages_use_configured_models_and_no_provider_storage(analysis, lesson, prepared):
    client = stub_client(analysis, lesson)
    settings = Settings(
        api_key="test-key", vision_model="vision-model", drawing_model="drawing-model"
    )
    generator = LessonGenerator(settings, client)
    result = await generator.generate(prepared)
    assert result.source == "ai"
    assert result.analysis == analysis
    assert result.groups == lesson.groups
    assert result.id.startswith("lesson-")
    assert result.id != lesson.id
    calls = client.responses.parse.call_args_list
    assert len(calls) == 2
    assert calls[0].kwargs["model"] == "vision-model"
    assert calls[1].kwargs["model"] == "drawing-model"
    assert calls[0].kwargs["text_format"] is Analysis
    assert calls[1].kwargs["text_format"] is Lesson
    for call in calls:
        assert call.kwargs["store"] is False
        image = call.kwargs["input"][1]["content"][1]
        assert image["type"] == "input_image"
        assert image["image_url"] == prepared.data_url
        assert "API_KEY" not in str(call.kwargs)


async def test_missing_key_cannot_be_disguised_as_a_demo(prepared):
    client = stub_client()
    generator = LessonGenerator(Settings(), client)
    with pytest.raises(GenerationError) as exc:
        await generator.generate(prepared)
    assert exc.value.status_code == 503
    client.responses.parse.assert_not_called()


async def test_unsuitable_photo_stops_before_construction(analysis_data, prepared):
    analysis_data.update(suitable=False, reason="Try a photo of one simple object without people.")
    client = stub_client(Analysis.model_validate(analysis_data))
    with pytest.raises(GenerationError) as exc:
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)
    assert exc.value.status_code == 422
    assert "without people" in exc.value.detail
    assert client.responses.parse.call_count == 1


@pytest.mark.parametrize("missing_stage", ["analysis", "lesson"])
async def test_refusals_or_missing_parsed_output_fail_cleanly(analysis, prepared, missing_stage):
    client = stub_client(None) if missing_stage == "analysis" else stub_client(analysis, None)
    with pytest.raises(GenerationError) as exc:
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)
    assert exc.value.status_code == (422 if missing_stage == "analysis" else 502)


async def test_invalid_analysis_output_rejected(prepared):
    client = stub_client({"subject": "dog", "svg": "<svg/>"})
    with pytest.raises(GenerationError) as exc:
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)
    assert exc.value.status_code == 502
    assert client.responses.parse.call_count == 1


async def test_preconstructed_invalid_analysis_is_revalidated(analysis, prepared):
    invalid = Analysis.model_construct(**{**analysis.model_dump(), "suitable": "true"})
    client = stub_client(invalid)
    with pytest.raises(GenerationError):
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)


@pytest.mark.parametrize("change", ["markup", "demo", "analysis", "subject", "duplicate"])
async def test_invalid_or_unfaithful_lesson_rejected(analysis, lesson_data, prepared, change):
    if change == "markup":
        lesson_data["svg"] = "<script>secret</script>"
    elif change == "demo":
        lesson_data["source"] = "demo"
    elif change == "analysis":
        lesson_data["analysis"]["composition"] = "A completely different composition."
    elif change == "subject":
        lesson_data["subject"] = "an unrelated horse"
    else:
        lesson_data["groups"][1]["strokes"][0]["id"] = "head"
    client = stub_client(analysis, lesson_data)
    with pytest.raises(GenerationError) as exc:
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)
    assert exc.value.status_code == 502
    assert "secret" not in exc.value.detail


async def test_preconstructed_invalid_lesson_is_revalidated(analysis, lesson, prepared):
    invalid = lesson.model_copy(update={"schema_version": "unexpected-version"})
    client = stub_client(analysis, invalid)
    with pytest.raises(GenerationError):
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)


def provider_error(error_type):
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    if error_type is APITimeoutError:
        return error_type(request)
    if error_type is APIConnectionError:
        return error_type(message="api key: secret", request=request)
    if error_type is APIError:
        return error_type("api key: secret", request=request, body=None)
    response = httpx.Response(503, request=request)
    return error_type("api key: secret", response=response, body={"secret": "photo-content"})


@pytest.mark.parametrize(
    "error_type,status",
    [
        (APITimeoutError, 504),
        (APIConnectionError, 503),
        (AuthenticationError, 503),
        (PermissionDeniedError, 503),
        (RateLimitError, 503),
        (APIError, 502),
    ],
)
async def test_provider_errors_are_safe_and_actionable(error_type, status, prepared):
    client = stub_client()
    client.responses.parse.side_effect = provider_error(error_type)
    with pytest.raises(GenerationError) as exc:
        await LessonGenerator(Settings(api_key="test-key"), client).generate(prepared)
    assert exc.value.status_code == status
    assert "secret" not in exc.value.detail
    assert "photo-content" not in exc.value.detail


async def test_total_pipeline_timeout_is_bounded(prepared):
    client = stub_client()

    async def delayed(**kwargs):
        await asyncio.sleep(0.05)

    client.responses.parse.side_effect = delayed
    settings = Settings(api_key="test-key", request_timeout_seconds=0.005)
    with pytest.raises(GenerationError) as exc:
        await LessonGenerator(settings, client).generate(prepared)
    assert exc.value.status_code == 504


def response_body(payload, index):
    return {
        "id": f"resp_mock_{index}",
        "object": "response",
        "created_at": 1700000000,
        "status": "completed",
        "model": "gpt-5.4",
        "output": [
            {
                "id": f"msg_mock_{index}",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(payload),
                        "annotations": [],
                    }
                ],
            }
        ],
        "parallel_tool_calls": True,
        "tools": [],
        "tool_choice": "auto",
        "store": False,
    }


async def test_real_official_sdk_parses_mocked_responses_without_paid_calls(
    analysis_data, lesson_data, prepared
):
    calls = []
    payloads = [analysis_data, lesson_data]

    def transport(request):
        assert request.url == "https://api.openai.com/v1/responses"
        body = json.loads(request.content)
        calls.append(body)
        assert body["store"] is False
        assert body["text"]["format"]["type"] == "json_schema"
        assert body["text"]["format"]["strict"] is True
        return httpx.Response(200, json=response_body(payloads[len(calls) - 1], len(calls)))

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(transport))
    client = AsyncOpenAI(api_key="test-key", http_client=http_client, max_retries=0)
    generator = LessonGenerator(Settings(api_key="test-key"), client)
    try:
        lesson = await generator.generate(prepared)
        assert lesson.subject == analysis_data["subject"]
        assert lesson.source == "ai"
        assert len(calls) == 2
    finally:
        await generator.close()


async def test_client_closed_on_shutdown():
    client = stub_client()
    generator = LessonGenerator(Settings(api_key="test-key"), client)
    await generator.close()
    client.close.assert_awaited_once()
