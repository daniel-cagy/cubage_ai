from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from product_estimator.estimate_product import estimate_product


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
KNOWN_MEASURE_TYPES = {"comprimento", "largura", "altura", "peso"}


def parse_known_measures(raw_known_measures: str) -> dict[str, float]:
    if not raw_known_measures.strip():
        return {}

    try:
        known_measures = json.loads(raw_known_measures)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="As medidas conhecidas precisam estar em JSON válido.",
        ) from exc

    if not isinstance(known_measures, list):
        raise HTTPException(
            status_code=400,
            detail="As medidas conhecidas precisam ser enviadas como uma lista.",
        )

    parsed_measures: dict[str, float] = {}

    for item in known_measures:
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=400,
                detail="Cada medida conhecida precisa ser um objeto.",
            )

        measure_type = item.get("tipo")
        measure_value = item.get("valor")

        if measure_type not in KNOWN_MEASURE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Tipo de medida conhecida inválido.",
            )

        if isinstance(measure_value, bool) or not isinstance(measure_value, (int, float)):
            raise HTTPException(
                status_code=400,
                detail="Valor de medida conhecida inválido.",
            )

        if measure_value <= 0:
            raise HTTPException(
                status_code=400,
                detail="Medidas conhecidas precisam ser maiores que zero.",
            )

        parsed_measures[measure_type] = float(measure_value)

    return parsed_measures

app = FastAPI(
    title="Cubage AI",
    description="API para estimar dimensões, peso e métricas logísticas de produtos embalados.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home() -> FileResponse:
    return FileResponse("index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/estimate")
async def estimate(
    image: UploadFile = File(...),
    description: str = Form(...),
    known_measures: str = Form("[]"),
    model: str = Form(DEFAULT_MODEL),
) -> dict[str, Any]:
    if not description.strip():
        raise HTTPException(status_code=400, detail="A descrição do produto é obrigatória.")

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado precisa ser uma imagem.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="A imagem enviada está vazia.")

    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="A imagem deve ter no máximo 10 MB.")

    parsed_known_measures = parse_known_measures(known_measures)

    suffix = Path(image.filename or "").suffix or ".jpg"
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(image_bytes)

        return estimate_product(
            image_path=temp_path,
            product_description=description.strip(),
            model=model,
            known_measures=parsed_known_measures,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Não foi possível estimar o produto: {exc}",
        ) from exc
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
