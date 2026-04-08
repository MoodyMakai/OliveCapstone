"""Image processing utilities for the Foodshare backend.

This module provides functions to process uploaded images, including square cropping,
resizing, and converting to optimized WebP format for efficient storage and delivery.
"""

import io
import logging

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def process_image(file_stream: bytes, target_size: int = 800) -> io.BytesIO:
    """Process an image to be square, resized, and converted to optimized WebP.

    This function performs the following operations:
    1. Opens the image from the input buffer.
    2. Converts it to RGB format (handling RGBA/CMYK).
    3. Crops the image to a centered square based on its shortest dimension.
    4. Resizes the image to the target dimensions using high-quality Lanczos filtering.
    5. Saves the resulting image to a BytesIO buffer as WebP with 80% quality.

    Args:
        file_stream (bytes): The input buffer containing raw image data.
        target_size (int): The target width and height for the square image. Defaults to 800.

    Returns:
        io.BytesIO: A buffer containing the processed WebP image data.

    Raises:
        Exception: If image processing fails.
    """
    try:
        # Load image using Pillow
        logger.debug(f"Attempting to process image of size {len(file_stream)} bytes")
        with Image.open(io.BytesIO(file_stream)) as img:
            logger.debug(f"Opened image: {img.format}, {img.size}, {img.mode}")
            # Handle orientation based on EXIF data
            img = ImageOps.exif_transpose(img)

            # Convert to RGB to ensure compatibility and remove transparency/CMYK issues
            img = img.convert("RGB")

            # 1. Square Crop (Center Crop)
            width, height = img.size
            if width > height:
                left = (width - height) // 2
                right = (width + height) // 2
                top = 0
                bottom = height
            else:
                left = 0
                right = width
                top = (height - width) // 2
                bottom = (height + width) // 2

            img = img.crop((left, top, right, bottom))

            # 2. Resize to target dimensions
            # Using LANCZOS (formerly ANTIALIAS) for highest quality downsampling
            img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

            # 3. Save as optimized WebP
            output = io.BytesIO()
            # Quality 80 provides excellent balance between size and visual fidelity
            img.save(output, format="WEBP", quality=80, method=6)  # method=6 is highest compression effort
            output.seek(0)

            logger.debug(f"Image processed successfully. Final size: {output.getbuffer().nbytes} bytes")
            return output

    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}", exc_info=True)
        raise
