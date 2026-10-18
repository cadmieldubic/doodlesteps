"""REST API for demo lessons and private, ephemeral photo generation."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

from .demos import DEMO_LESSONS, get_demo
from .generation import GenerationError, LessonGenerator
from .images import SUPPORTED_FORMATS, ImageValidationError, prepare_image
from .limits import GenerationGate
from .middleware import UploadLimitMiddleware
from .models import Lesson
from .settings import Settings


def create_app(
    settings: Settings | None = None,
    generator: Any | None = None,
    gate: GenerationGate | None = None,
) -> FastAPI:
    settings = settings or Settings.from_environment()
    lesson_generator = generator or LessonGenerator(settings)
    generation_gate = gate or GenerationGate(settings.requests_per_minute, settings.max_concurrent)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        if generator is None:
            await lesson_generator.close()

    app = FastAPI(
        title="DoodleSteps",
        version="1.0.0",
        description="Private, adult-supervised prototype. Use non-personal photographs only.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.generator = lesson_generator
    app.state.gate = generation_gate
    app.add_middleware(UploadLimitMiddleware, max_upload_bytes=settings.max_upload_bytes)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    @app.middleware("http")
    async def private_responses(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_: Request, __: RequestValidationError):
        # Avoid returning uploaded data or internal validation context.
        return JSONResponse(
            {"detail": "The request is invalid. Please choose a photograph and try again."},
            status_code=422,
        )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/config")
    async def config() -> dict[str, Any]:
        return {
            "ai_available": settings.ai_available,
            "max_upload_bytes": settings.max_upload_bytes,
            "supported_formats": list(SUPPORTED_FORMATS),
        }

    @app.get("/api/demos", response_model=list[Lesson])
    async def demos() -> list[Lesson]:
        return DEMO_LESSONS

    @app.get("/api/demos/{lesson_id}", response_model=Lesson)
    async def demo(lesson_id: str) -> Lesson:
        lesson = get_demo(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="That demo lesson was not found.")
        return lesson

    @app.post(
        "/api/lessons",
        response_model=Lesson,
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "type": "object",
                            "properties": {"image": {"type": "string", "format": "binary"}},
                            "required": ["image"],
                        }
                    }
                },
            }
        },
    )
    async def generate_lesson(request: Request) -> Lesson:
        # CORS controls response visibility, not whether a browser sends a simple
        # multipart POST. Reject foreign origins before parsing or paid AI work.
        # Origin-absent local scripts/CLI clients remain supported.
        origin = request.headers.get("origin", "").strip()
        if origin and origin not in settings.cors_origins:
            raise HTTPException(
                status_code=403,
                detail="Photo lessons can only be requested from the configured local app.",
            )
        if not settings.ai_available:
            raise HTTPException(
                status_code=503,
                detail="Live photo lessons are unavailable. An adult developer can configure "
                "OPENAI_API_KEY on the backend; the labeled demo lessons work now.",
            )
        content_type = request.headers.get("content-type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            raise HTTPException(
                status_code=415, detail="Send the photograph as multipart form field 'image'."
            )
        form = None
        try:
            # Keep this bounded upload in memory instead of spooling photographs to disk.
            parser = MultiPartParser(
                headers=request.headers,
                stream=request.stream(),
                max_files=1,
                max_fields=0,
                max_part_size=settings.max_upload_bytes,
            )
            parser.spool_max_size = settings.max_upload_bytes + 64 * 1024 + 1
            form = await parser.parse()
            fields = form.multi_items()
            if (
                len(fields) != 1
                or fields[0][0] != "image"
                or not isinstance(fields[0][1], UploadFile)
            ):
                raise HTTPException(
                    status_code=422, detail="Choose one photograph using the 'image' field."
                )
            image = fields[0][1]
            data = await image.read(settings.max_upload_bytes + 1)
            prepared = await run_in_threadpool(prepare_image, data, image.content_type, settings)
        except MultiPartException as exc:
            raise HTTPException(
                status_code=400, detail="Choose one photograph using the 'image' field."
            ) from exc
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        finally:
            if form is not None:
                await form.close()

        # Ignore forwarding headers: clients cannot spoof a new rate-limit identity.
        client = request.client.host if request.client else "local"
        reserved = False
        try:
            generation_gate.reserve(client)
            reserved = True
            return await lesson_generator.generate(prepared)
        except GenerationError as exc:
            headers = {"Retry-After": "60"} if exc.status_code in (429, 503) else None
            raise HTTPException(
                status_code=exc.status_code, detail=exc.detail, headers=headers
            ) from exc
        finally:
            if reserved:
                generation_gate.release()

    return app


app = create_app()
