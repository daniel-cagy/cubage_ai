#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from shutil import copy2

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from product_estimator.image_processing import (  # noqa: E402
    IMAGE_PROCESSING_MODE_ORIGINAL,
    IMAGE_PROCESSING_MODE_QUANTIZED,
    IMAGE_PROCESSING_MODE_RESIZED,
    process_image,
)

MODES = (
    IMAGE_PROCESSING_MODE_ORIGINAL,
    IMAGE_PROCESSING_MODE_RESIZED,
    IMAGE_PROCESSING_MODE_QUANTIZED,
)

EXTENSIONS_BY_MIME_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

LABELS_BY_MODE = {
    IMAGE_PROCESSING_MODE_ORIGINAL: "Original",
    IMAGE_PROCESSING_MODE_RESIZED: "Redimensionada",
    IMAGE_PROCESSING_MODE_QUANTIZED: "Quantizada",
}


@dataclass
class ProcessedImage:
    mode: str
    label: str
    path: Path
    mime_type: str
    width: int
    height: int
    bytes_size: int
    reduction_percent: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera previews da imagem original, redimensionada e quantizada."
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Caminho da imagem de entrada.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tests/results/image_processing_preview"),
        help="Diretorio onde os arquivos serao salvos.",
    )
    return parser.parse_args()


def get_extension(mime_type: str) -> str:
    return EXTENSIONS_BY_MIME_TYPE.get(mime_type, ".img")


def inspect_image(image_bytes: bytes) -> tuple[int, int]:
    with Image.open(BytesIO(image_bytes)) as image:
        return image.size


def save_processed_images(image_path: Path, output_dir: Path) -> list[ProcessedImage]:
    output_dir.mkdir(parents=True, exist_ok=True)
    original_size = image_path.stat().st_size
    processed_images = []

    for mode in MODES:
        image_bytes, mime_type = process_image(image_path, mode)
        width, height = inspect_image(image_bytes)
        extension = get_extension(mime_type)
        output_path = output_dir / f"{image_path.stem}_{mode}{extension}"
        output_path.write_bytes(image_bytes)

        reduction_percent = 0.0
        if original_size > 0:
            reduction_percent = (1 - (len(image_bytes) / original_size)) * 100

        processed_images.append(
            ProcessedImage(
                mode=mode,
                label=LABELS_BY_MODE[mode],
                path=output_path,
                mime_type=mime_type,
                width=width,
                height=height,
                bytes_size=len(image_bytes),
                reduction_percent=reduction_percent,
            )
        )

    copy2(image_path, output_dir / f"{image_path.stem}_source{image_path.suffix}")
    return processed_images


def draw_multiline_text(draw: ImageDraw.ImageDraw, position: tuple[int, int], lines: list[str], font: ImageFont.ImageFont) -> None:
    x, y = position
    for line in lines:
        draw.text((x, y), line, fill=(22, 28, 36), font=font)
        y += 20


def create_comparison_image(processed_images: list[ProcessedImage], output_path: Path) -> None:
    tile_width = 380
    tile_height = 470
    padding = 24
    image_area_height = 320
    canvas_width = tile_width * len(processed_images)
    canvas_height = tile_height

    canvas = Image.new("RGB", (canvas_width, canvas_height), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for index, processed in enumerate(processed_images):
        x0 = index * tile_width
        panel_box = (x0 + 10, 10, x0 + tile_width - 10, tile_height - 10)
        draw.rounded_rectangle(panel_box, radius=8, fill=(255, 255, 255), outline=(210, 218, 228))

        with Image.open(processed.path) as image:
            preview = image.convert("RGB")
            preview.thumbnail((tile_width - 2 * padding, image_area_height), Image.Resampling.LANCZOS)

        image_x = x0 + (tile_width - preview.width) // 2
        image_y = 34 + (image_area_height - preview.height) // 2
        canvas.paste(preview, (image_x, image_y))

        size_kb = processed.bytes_size / 1024
        lines = [
            processed.label,
            f"{processed.width} x {processed.height}px",
            f"{size_kb:.1f} KB | {processed.mime_type}",
            f"Reducao: {processed.reduction_percent:.1f}%",
        ]
        draw_multiline_text(draw, (x0 + padding, image_area_height + 48), lines, font)

    canvas.save(output_path, format="PNG", optimize=True)


def write_summary(processed_images: list[ProcessedImage], output_path: Path) -> None:
    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "mode",
                "file",
                "mime_type",
                "width",
                "height",
                "bytes",
                "kilobytes",
                "reduction_percent",
            ],
        )
        writer.writeheader()
        for processed in processed_images:
            writer.writerow(
                {
                    "mode": processed.mode,
                    "file": str(processed.path),
                    "mime_type": processed.mime_type,
                    "width": processed.width,
                    "height": processed.height,
                    "bytes": processed.bytes_size,
                    "kilobytes": round(processed.bytes_size / 1024, 2),
                    "reduction_percent": round(processed.reduction_percent, 2),
                }
            )


def main() -> None:
    args = parse_args()
    image_path = args.image
    output_dir = args.output_dir

    if not image_path.exists():
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")

    processed_images = save_processed_images(image_path, output_dir)
    comparison_path = output_dir / f"{image_path.stem}_comparison.png"
    summary_path = output_dir / f"{image_path.stem}_summary.csv"

    create_comparison_image(processed_images, comparison_path)
    write_summary(processed_images, summary_path)

    print(f"Arquivos gerados em: {output_dir}")
    print(f"Comparacao visual: {comparison_path}")
    print(f"Resumo CSV: {summary_path}")
    for processed in processed_images:
        print(
            f"- {processed.label}: {processed.path} "
            f"({processed.width}x{processed.height}px, "
            f"{processed.bytes_size / 1024:.1f} KB, "
            f"reducao {processed.reduction_percent:.1f}%)"
        )


if __name__ == "__main__":
    main()
