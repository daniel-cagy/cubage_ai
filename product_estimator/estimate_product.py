#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any
from product_estimator.schema import MEASUREMENT_SCHEMA
from product_estimator.prompt import SYSTEM_PROMPT

from openai import OpenAI


def image_to_data_url(image_path: Path) -> str:
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def estimate_product(image_path: Path, product_description: str, model: str) -> dict[str, Any]:
    client = OpenAI()

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Descrição textual do produto:\n"
                            f"{product_description}\n\n"
                            "Analise também a imagem anexada."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_to_data_url(image_path),
                    },
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                **MEASUREMENT_SCHEMA,
            }
        },
    )

    return json.loads(response.output_text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estima dimensões e peso de um produto usando imagem + descrição."
    )
    parser.add_argument("image", type=Path, help="Caminho da imagem do produto.")
    parser.add_argument(
        "description",
        help="Descrição textual do produto. Use aspas se tiver espaços.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        help="Modelo da OpenAI. Padrão: OPENAI_MODEL ou gpt-5.5.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Arquivo .json para salvar o resultado. Se omitido, imprime no terminal.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = estimate_product(
        image_path=args.image,
        product_description=args.description,
        model=args.model,
    )
    pretty_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        args.output.write_text(pretty_json + "\n", encoding="utf-8")
    else:
        print(pretty_json)
