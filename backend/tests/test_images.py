import io

import pytest
from backend.app.images import ImageValidationError, prepare_image
from backend.app.settings import Settings
from PIL import Image, PngImagePlugin


@pytest.mark.parametrize(
    "format,mime", [("JPEG", "image/jpeg"), ("PNG", "image/png"), ("WEBP", "image/webp")]
)
def test_supported_formats_reencode_as_jpeg(format, mime):
    buffer = io.BytesIO()
    Image.new("RGB", (100, 60), "lavender").save(buffer, format=format)
    prepared = prepare_image(buffer.getvalue(), mime, Settings())
    with Image.open(io.BytesIO(prepared.data)) as output:
        assert output.format == "JPEG"
        assert output.mode == "RGB"
        assert output.size == (100, 60)
    assert prepared.data_url.startswith("data:image/jpeg;base64,")


def test_resize_keeps_aspect_ratio(png_bytes):
    prepared = prepare_image(png_bytes, "image/png", Settings(max_image_dimension=60))
    assert (prepared.width, prepared.height) == (60, 40)


def test_exif_gps_and_comments_are_removed():
    image = Image.new("RGB", (80, 40), "white")
    exif = Image.Exif()
    exif[270] = "Private image description"
    exif[274] = 6
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    prepared = prepare_image(buffer.getvalue(), "image/jpeg", Settings())
    with Image.open(io.BytesIO(prepared.data)) as output:
        assert output.size == (40, 80)
        assert not output.getexif()
        assert "exif" not in output.info
        assert "comment" not in output.info
        assert "icc_profile" not in output.info
    assert b"Private image description" not in prepared.data


def test_png_text_metadata_removed():
    buffer = io.BytesIO()
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("location", "private location")
    Image.new("RGBA", (40, 40), (0, 0, 0, 0)).save(buffer, "PNG", pnginfo=metadata)
    prepared = prepare_image(buffer.getvalue(), "image/png", Settings())
    with Image.open(io.BytesIO(prepared.data)) as output:
        assert not output.getexif()
        assert output.getpixel((20, 20)) == (255, 255, 255)
    assert b"private location" not in prepared.data


@pytest.mark.parametrize("mime", ["image/svg+xml", "image/gif", "text/plain", "", None])
def test_unsupported_mime_rejected(png_bytes, mime):
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(png_bytes, mime, Settings())
    assert exc.value.status_code == 415


def test_mime_content_mismatch_is_rejected(png_bytes):
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(png_bytes, "image/jpeg", Settings())
    assert exc.value.status_code == 415


@pytest.mark.parametrize(
    "data", [b"", b"<svg onload='alert(1)'/>", b"not a photo", b"\x89PNG\r\n\x1a\n"]
)
def test_empty_corrupt_and_markup_files_rejected(data):
    with pytest.raises(ImageValidationError):
        prepare_image(data, "image/png", Settings())


def test_oversized_upload_is_rejected_before_opening(png_bytes):
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(png_bytes, "image/png", Settings(max_upload_bytes=1))
    assert exc.value.status_code == 413


def test_pixel_limit_is_checked_before_decode(png_bytes):
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(png_bytes, "image/png", Settings(max_image_pixels=100))
    assert exc.value.status_code == 413


def test_decompression_bomb_warning_becomes_rejection(monkeypatch, png_bytes):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 5000)
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(png_bytes, "image/png", Settings())
    assert exc.value.status_code == 413


def test_tiny_image_gets_helpful_rejection():
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, "PNG")
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(buffer.getvalue(), "image/png", Settings())
    assert exc.value.status_code == 422


def test_animated_webp_rejected():
    buffer = io.BytesIO()
    frames = [Image.new("RGB", (40, 40), color) for color in ("red", "blue")]
    frames[0].save(buffer, "WEBP", save_all=True, append_images=frames[1:], duration=100, loop=0)
    with pytest.raises(ImageValidationError) as exc:
        prepare_image(buffer.getvalue(), "image/webp", Settings())
    assert exc.value.status_code == 415
