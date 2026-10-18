"""Validate and sanitize photographs entirely in memory before any AI request."""

import base64
import io
import warnings
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError

from .settings import Settings

SUPPORTED_FORMATS = ("image/jpeg", "image/png", "image/webp")
FORMAT_MIMES = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class ImageValidationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


@dataclass(frozen=True)
class PreparedImage:
    data: bytes
    width: int
    height: int

    @property
    def data_url(self) -> str:
        return "data:image/jpeg;base64," + base64.b64encode(self.data).decode("ascii")


def prepare_image(data: bytes, content_type: str | None, settings: Settings) -> PreparedImage:
    """Verify true type/pixel size, apply orientation, flatten, resize and re-encode.

    Reconstructing a fresh RGB image drops EXIF, GPS, ICC, comments and text chunks.
    A white background keeps transparent PNGs legible to the vision model.
    """
    if not data:
        raise ImageValidationError("Choose a photograph before starting your lesson.")
    if len(data) > settings.max_upload_bytes:
        raise ImageValidationError("This photo is too large. Choose a smaller photo.", 413)
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if mime not in SUPPORTED_FORMATS:
        raise ImageValidationError("Use a JPEG, PNG, or WebP photograph.", 415)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as original:
                if FORMAT_MIMES.get(original.format or "") != mime:
                    raise ImageValidationError(
                        "The file contents do not match its image format.", 415
                    )
                if original.width * original.height > settings.max_image_pixels:
                    raise ImageValidationError(
                        "This photo has too many pixels. Choose a smaller photo.", 413
                    )
                if original.width < 32 or original.height < 32:
                    raise ImageValidationError(
                        "This photo is too small. Choose a clearer photo.", 422
                    )
                if getattr(original, "n_frames", 1) != 1:
                    raise ImageValidationError(
                        "Choose a still photograph instead of an animated image.", 415
                    )
                original.verify()
            with Image.open(io.BytesIO(data)) as original:
                oriented = ImageOps.exif_transpose(original)
                oriented.thumbnail(
                    (settings.max_image_dimension, settings.max_image_dimension),
                    resample=Image.Resampling.LANCZOS,
                )
                rgba = oriented.convert("RGBA")
                clean = Image.new("RGB", rgba.size, "white")
                clean.paste(rgba, mask=rgba.getchannel("A"))
                output = io.BytesIO()
                clean.save(output, format="JPEG", quality=88, optimize=True)
                return PreparedImage(output.getvalue(), clean.width, clean.height)
    except ImageValidationError:
        raise
    except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
        raise ImageValidationError(
            "This photo has too many pixels. Choose a smaller photo.", 413
        ) from exc
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as exc:
        raise ImageValidationError(
            "We could not read this photo. Choose a valid JPEG, PNG, or WebP."
        ) from exc
