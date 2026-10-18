"""Bound image request bodies before multipart parsing, including chunked input."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class UploadLimitMiddleware:
    """Buffer only a bounded multipart request in memory before handing it to FastAPI.

    Inspecting Content-Length alone is insufficient for chunked or dishonest
    clients. This middleware counts actual bytes regardless of those headers.
    """

    def __init__(self, app: ASGIApp, max_upload_bytes: int):
        self.app = app
        # A little room for multipart boundaries/headers, not another uploaded file.
        self.max_request_bytes = max_upload_bytes + 64 * 1024

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") != "/api/lessons"
        ):
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        if b"content-length" in headers:
            try:
                content_length = int(headers[b"content-length"])
            except ValueError:
                await JSONResponse({"detail": "Invalid request length."}, status_code=400)(
                    scope, receive, send
                )
                return
            if content_length < 0:
                await JSONResponse({"detail": "Invalid request length."}, status_code=400)(
                    scope, receive, send
                )
                return
            if content_length > self.max_request_bytes:
                await self._too_large(scope, receive, send)
                return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_request_bytes:
                await self._too_large(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)

    @staticmethod
    async def _too_large(scope: Scope, receive: Receive, send: Send) -> None:
        await JSONResponse(
            {"detail": "This photo is too large. Choose a smaller photo."}, status_code=413
        )(scope, receive, send)
