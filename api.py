from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from product_estimator.estimate_product import estimate_product


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(
    title="Cubage AI",
    description="API para estimar dimensões, peso e métricas logísticas de produtos embalados.",
    version="0.1.0",
)


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
