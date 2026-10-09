import pytest
from backend.app.middleware import UploadLimitMiddleware


async def send_request(chunks, headers=(), path="/api/lessons"):
    called = []
    sent = []
    messages = iter(
        [
            {"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1}
            for index, chunk in enumerate(chunks)
        ]
    )

    async def receive():
        return next(messages)

    async def send(message):
        sent.append(message)

    async def downstream(scope, receive, send):
        called.append(await receive())

    scope = {"type": "http", "method": "POST", "path": path, "headers": list(headers)}
    await UploadLimitMiddleware(downstream, max_upload_bytes=10)(scope, receive, send)
    return called, sent


async def test_chunked_upload_is_bounded_without_content_length():
    called, sent = await send_request([b"a" * 40000, b"b" * 40000])
    assert not called
    assert sent[0]["status"] == 413


async def test_dishonest_small_content_length_cannot_bypass_limit():
    called, sent = await send_request([b"a" * 70000], [(b"content-length", b"1")])
    assert not called
    assert sent[0]["status"] == 413


async def test_large_declared_body_is_rejected_before_reading():
    called, sent = await send_request([], [(b"content-length", b"70000")])
    assert not called
    assert sent[0]["status"] == 413


@pytest.mark.parametrize("value", [b"bad", b"-1"])
async def test_invalid_length_is_rejected(value):
    called, sent = await send_request([], [(b"content-length", value)])
    assert not called
    assert sent[0]["status"] == 400


async def test_valid_chunks_are_replayed_exactly_once():
    called, sent = await send_request([b"abc", b"def"])
    assert called == [{"type": "http.request", "body": b"abcdef", "more_body": False}]
    assert not sent
