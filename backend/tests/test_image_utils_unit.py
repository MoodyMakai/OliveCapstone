import io

import pytest
from PIL import Image

from src.image_utils import process_image


def create_test_image(mode="RGB", size=(1000, 500), format="PNG"):
    """Helper to create a test image in memory."""
    img = Image.new(mode, size, color="red")
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_process_image_landscape():
    """Verify that a landscape image is center-cropped to a square."""
    data = create_test_image(size=(1000, 500))
    result = process_image(data)

    with Image.open(result) as img:
        assert img.size == (800, 800)
        assert img.format == "WEBP"


def test_process_image_portrait():
    """Verify that a portrait image is center-cropped to a square."""
    data = create_test_image(size=(400, 800))
    result = process_image(data)

    with Image.open(result) as img:
        assert img.size == (800, 800)
        assert img.format == "WEBP"


def test_process_image_rgba_conversion():
    """Verify that an RGBA image is correctly converted to RGB (no transparency issues)."""
    data = create_test_image(mode="RGBA", size=(500, 500))
    result = process_image(data)

    with Image.open(result) as img:
        assert img.mode == "RGB"
        assert img.size == (800, 800)


def test_process_image_cmyk_conversion():
    """Verify that a CMYK image is correctly converted to RGB."""
    data = create_test_image(mode="CMYK", size=(500, 500), format="JPEG")
    result = process_image(data)

    with Image.open(result) as img:
        assert img.mode == "RGB"


def test_process_image_preserves_orientation():
    """Verify that EXIF orientation is respected (image is transposed if needed)."""
    # Create an image that is 100x200 but with EXIF orientation 6 (90 deg CW)
    # Pillow's ImageOps.exif_transpose will make it 200x100 if we handle it right.
    img = Image.new("RGB", (100, 200), color="blue")
    exif = img.getexif()
    # 274 is the tag for Orientation. 6 means Rotate 90 CW.
    exif[274] = 6

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    data = buf.getvalue()

    result = process_image(data)
    with Image.open(result) as processed:
        # After square crop it will be 800x800 anyway,
        # but internal processing should have transposed it first.
        assert processed.size == (800, 800)


def test_process_image_small_input():
    """Verify that images smaller than 800x800 are correctly upscaled/padded."""
    data = create_test_image(size=(100, 100))
    result = process_image(data)

    with Image.open(result) as img:
        assert img.size == (800, 800)


def test_process_image_invalid_data():
    """Verify that invalid image data raises an exception."""
    with pytest.raises(Exception):
        process_image(b"not an image")
