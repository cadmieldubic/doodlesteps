"""Two structured-output AI stages, validated again at the trust boundary."""

import asyncio
from typing import Any
from uuid import uuid4

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)
from pydantic import ValidationError

from .images import PreparedImage
from .models import Analysis, Lesson
from .prompts import ANALYSIS_PROMPT, DRAWING_PROMPT
from .settings import Settings


class GenerationError(Exception):
    def __init__(self, detail: str, status_code: int = 502):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class LessonGenerator:
    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client
        if self.client is None and settings.ai_available:
            self.client = AsyncOpenAI(
                api_key=settings.api_key,
                timeout=settings.request_timeout_seconds,
                max_retries=0,
            )

    async def close(self) -> None:
        if self.client is not None:
            await self.client.close()

    async def generate(self, image: PreparedImage) -> Lesson:
        if self.client is None or not self.settings.ai_available:
            raise GenerationError(
                "Live photo lessons are unavailable. An adult developer can configure "
                "OPENAI_API_KEY on the backend; the labeled demo lessons work now.",
                503,
            )
        try:
            async with asyncio.timeout(self.settings.request_timeout_seconds):
                return await self._generate(image)
        except GenerationError:
            raise
        except (TimeoutError, APITimeoutError) as exc:
            raise GenerationError(
                "The drawing teacher took too long. Please try again shortly.", 504
            ) from exc
        except (AuthenticationError, PermissionDeniedError) as exc:
            raise GenerationError(
                "Live AI is not authorized. Ask an adult developer to check backend configuration.",
                503,
            ) from exc
        except RateLimitError as exc:
            raise GenerationError(
                "The drawing teacher is busy. Please try again in a minute.", 503
            ) from exc
        except APIConnectionError as exc:
            raise GenerationError(
                "We could not reach the drawing teacher. Please try again shortly.", 503
            ) from exc
        except (ValidationError, ValueError, TypeError, AttributeError) as exc:
            raise GenerationError(
                "The AI lesson did not pass our drawing checks. Please try a simpler photo."
            ) from exc
        except (APIError, OpenAIError) as exc:
            raise GenerationError(
                "The drawing teacher could not finish this lesson. Please try again shortly."
            ) from exc

    async def _generate(self, image: PreparedImage) -> Lesson:
        image_content = {"type": "input_image", "image_url": image.data_url, "detail": "high"}
        understanding = await self.client.responses.parse(
            model=self.settings.vision_model,
            input=[
                {"role": "system", "content": ANALYSIS_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Understand this photograph for one beginner drawing lesson.",
                        },
                        image_content,
                    ],
                },
            ],
            text_format=Analysis,
            store=False,
            max_output_tokens=min(self.settings.max_output_tokens, 2400),
        )
        if understanding.output_parsed is None:
            raise GenerationError(
                "This photo could not be understood. Try a clearer photo of one simple object.", 422
            )
        parsed_analysis = understanding.output_parsed
        if isinstance(parsed_analysis, Analysis):
            analysis = Analysis.model_validate_json(parsed_analysis.model_dump_json())
        else:
            analysis = Analysis.model_validate(parsed_analysis)
        if not analysis.suitable:
            # Use a bounded teacher reason; never echo provider errors or photo contents.
            reason = analysis.reason or "Choose a clearer photo of one simple non-personal object."
            raise GenerationError(reason, 422)

        construction = await self.client.responses.parse(
            model=self.settings.drawing_model,
            input=[
                {"role": "system", "content": DRAWING_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Construct the shared blueprint using this exact Analysis:\n"
                            + analysis.model_dump_json(),
                        },
                        image_content,
                    ],
                },
            ],
            text_format=Lesson,
            store=False,
            max_output_tokens=self.settings.max_output_tokens,
        )
        if construction.output_parsed is None:
            raise GenerationError("The AI could not create a checked drawing. Try a simpler photo.")
        # JSON round-trip ensures even a constructed Pydantic instance is revalidated.
        parsed = construction.output_parsed
        if isinstance(parsed, Lesson):
            lesson = Lesson.model_validate_json(parsed.model_dump_json())
        else:
            lesson = Lesson.model_validate(parsed)
        if (
            lesson.source != "ai"
            or lesson.analysis != analysis
            or lesson.subject != analysis.subject
        ):
            raise GenerationError(
                "The drawing did not stay faithful to the photo analysis. Please try again."
            )
        return lesson.model_copy(update={"id": "lesson-" + uuid4().hex})
