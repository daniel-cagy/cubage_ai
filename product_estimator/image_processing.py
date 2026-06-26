import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


DEFAULT_MAX_SIZE = 1024
DEFAULT_JPEG_QUALITY = 85
DEFAULT_QUANTIZE_COLORS = 128
MIN_OPTIMIZATION_GAIN = 0.05
IMAGE_PROCESSING_MODE_ORIGINAL = "original"
IMAGE_PROCESSING_MODE_RESIZED = "resized"
IMAGE_PROCESSING_MODE_QUANTIZED = "quantized"
DEFAULT_IMAGE_PROCESSING_MODE = IMAGE_PROCESSING_MODE_RESIZED
IMAGE_PROCESSING_MODES = {
    IMAGE_PROCESSING_MODE_ORIGINAL,
    IMAGE_PROCESSING_MODE_RESIZED,
    IMAGE_PROCESSING_MODE_QUANTIZED,
}


def get_image_mime_type(image_format: str | None) -> str:
    if image_format == "PNG":
        return "image/png"
    if image_format == "WEBP":
        return "image/webp"
    return "image/jpeg"


def image_to_data_url(
    image_path: Path,
    processing_mode: str = DEFAULT_IMAGE_PROCESSING_MODE,
) -> str:
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    image_bytes, mime_type = process_image(image_path, processing_mode)
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def process_image(
    image_path: Path,
    processing_mode: str = DEFAULT_IMAGE_PROCESSING_MODE,
) -> tuple[bytes, str]:
    if processing_mode == IMAGE_PROCESSING_MODE_ORIGINAL:
        return original_image(image_path)

    if processing_mode == IMAGE_PROCESSING_MODE_RESIZED:
        return optimize_image(image_path)

    if processing_mode == IMAGE_PROCESSING_MODE_QUANTIZED:
        return quantize_image(image_path)

    raise ValueError(f"Modo de processamento de imagem inválido: {processing_mode}")


def original_image(image_path: Path) -> tuple[bytes, str]:
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    image_bytes = image_path.read_bytes()
    with Image.open(image_path) as image:
        mime_type = get_image_mime_type(image.format)

    return image_bytes, mime_type


def optimize_image(image_path: Path,
    max_size: int = DEFAULT_MAX_SIZE,
    quality: int = DEFAULT_JPEG_QUALITY,
    min_gain: float = MIN_OPTIMIZATION_GAIN,
) -> tuple[bytes, str]:
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    original_bytes = image_path.read_bytes()

    with Image.open(image_path) as image:
        original_format = image.format
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image.thumbnail((max_size, max_size))

        buffer = BytesIO()
        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
        )

    optimized_bytes = buffer.getvalue()
    minimum_expected_size = len(original_bytes) * (1 - min_gain)

    if len(optimized_bytes) >= minimum_expected_size and original_format in {"JPEG", "PNG", "WEBP"}:
        return original_bytes, get_image_mime_type(original_format)

    return optimized_bytes, "image/jpeg"


def quantize_image(
    image_path: Path,
    max_size: int = DEFAULT_MAX_SIZE,
    colors: int = DEFAULT_QUANTIZE_COLORS,
) -> tuple[bytes, str]:
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    if colors < 2 or colors > 256:
        raise ValueError("'colors' deve estar entre 2 e 256.")

    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image.thumbnail((max_size, max_size))
        image = image.quantize(
            colors=colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG,
        )

        buffer = BytesIO()
        image.save(
            buffer,
            format="PNG",
            optimize=True,
        )

    return buffer.getvalue(), "image/png"
