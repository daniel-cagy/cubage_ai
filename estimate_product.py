#!/usr/bin/env python3
"""Estimate product dimensions and weight from an image plus description."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """Você é um especialista em estimativa dimensional e logística de produtos a partir de imagem e descrição textual.

Sua tarefa é analisar a imagem fornecida junto com a descrição do produto e inferir, da forma mais realista possível:

1. Dimensões do produto:
   - comprimento
   - largura
   - altura
   - unidade em centímetros

2. Peso estimado:
   - peso líquido aproximado do produto
   - unidade em quilogramas

3. Dimensões e peso da embalagem, quando possível:
   - comprimento, largura e altura da embalagem
   - peso bruto aproximado
   - unidade em centímetros e quilogramas

Você deve usar todas as pistas disponíveis:
- escala visual relativa;
- formato do objeto;
- materiais aparentes;
- categoria do produto;
- proporções típicas de produtos semelhantes;
- informações explícitas ou implícitas da descrição;
- presença de componentes, acessórios, cabos, estrutura, embalagem ou partes metálicas/plásticas;
- comparação com objetos comuns, quando houver.

Regras importantes:

- Não afirme medidas como se fossem exatas.
- Sempre trate as dimensões e pesos como estimativas.
- Quando a imagem ou descrição forem insuficientes, indique claramente a incerteza.
- Se houver ambiguidade, forneça uma faixa provável em vez de um único valor.
- Não invente informações técnicas específicas que não possam ser inferidas.
- Se o produto estiver parcialmente visível, em perspectiva distorcida, sem escala ou com baixa qualidade de imagem, reduza a confiança.
- Considere que produtos vendidos online geralmente têm embalagem maior que o produto, com margem para proteção.
- Diferencie o produto em si da embalagem.
- Quando não for possível estimar com segurança, diga isso explicitamente e explique o motivo.
- Use bom senso logístico: pesos e dimensões devem ser fisicamente plausíveis para o tipo de produto.

Retorne sempre a resposta em JSON válido, sem markdown, sem comentários fora do JSON.

Use exatamente este formato:

{
  "produto_identificado": "nome ou categoria provável do produto",
  "descricao_resumida": "breve descrição do que foi observado",
  "dimensoes_produto_estimadas_cm": {
    "comprimento": {
      "min": 0,
      "max": 0,
      "estimativa": 0
    },
    "largura": {
      "min": 0,
      "max": 0,
      "estimativa": 0
    },
    "altura": {
      "min": 0,
      "max": 0,
      "estimativa": 0
    }
  },
  "peso_liquido_estimado_kg": {
    "min": 0,
    "max": 0,
    "estimativa": 0
  },
  "dimensoes_embalagem_estimadas_cm": {
    "comprimento": {
      "min": 0,
      "max": 0,
      "estimativa": 0
    },
    "largura": {
      "min": 0,
      "max": 0,
      "estimativa": 0
    },
    "altura": {
      "min": 0,
      "max": 0,
      "estimativa": 0
    }
  },
  "peso_bruto_estimado_kg": {
    "min": 0,
    "max": 0,
    "estimativa": 0
  },
  "nivel_confianca": "baixo | medio | alto",
  "principais_pistas_usadas": [
    "pista 1",
    "pista 2",
    "pista 3"
  ],
  "fatores_de_incerteza": [
    "fator 1",
    "fator 2"
  ],
  "observacoes": "comentários relevantes sobre limitações, premissas ou riscos da estimativa"
}

Critérios para nível de confiança:

- "alto": imagem clara, produto inteiro visível, categoria conhecida, descrição coerente e boa noção de escala.
- "medio": produto visível e categoria identificável, mas sem escala explícita ou com alguma ambiguidade.
- "baixo": imagem ruim, produto parcial, sem referência de escala, categoria ambígua ou descrição insuficiente.

Se a descrição textual trouxer medidas explícitas, priorize essas medidas sobre a inferência visual, mas valide se parecem compatíveis com a imagem.
Se houver conflito entre imagem e descrição, indique o conflito em "observacoes" e reduza o nível de confiança."""


MEASUREMENT_SCHEMA: dict[str, Any] = {
    "name": "estimativa_dimensional_produto",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "produto_identificado",
            "descricao_resumida",
            "dimensoes_produto_estimadas_cm",
            "peso_liquido_estimado_kg",
            "dimensoes_embalagem_estimadas_cm",
            "peso_bruto_estimado_kg",
            "nivel_confianca",
            "principais_pistas_usadas",
            "fatores_de_incerteza",
            "observacoes",
        ],
        "properties": {
            "produto_identificado": {"type": "string"},
            "descricao_resumida": {"type": "string"},
            "dimensoes_produto_estimadas_cm": {"$ref": "#/$defs/dimensoes"},
            "peso_liquido_estimado_kg": {"$ref": "#/$defs/faixa_numerica"},
            "dimensoes_embalagem_estimadas_cm": {"$ref": "#/$defs/dimensoes"},
            "peso_bruto_estimado_kg": {"$ref": "#/$defs/faixa_numerica"},
            "nivel_confianca": {"type": "string", "enum": ["baixo", "medio", "alto"]},
            "principais_pistas_usadas": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
            "fatores_de_incerteza": {
                "type": "array",
                "items": {"type": "string"},
            },
            "observacoes": {"type": "string"},
        },
        "$defs": {
            "faixa_numerica": {
                "type": "object",
                "additionalProperties": False,
                "required": ["min", "max", "estimativa"],
                "properties": {
                    "min": {"type": "number", "minimum": 0},
                    "max": {"type": "number", "minimum": 0},
                    "estimativa": {"type": "number", "minimum": 0},
                },
            },
            "dimensoes": {
                "type": "object",
                "additionalProperties": False,
                "required": ["comprimento", "largura", "altura"],
                "properties": {
                    "comprimento": {"$ref": "#/$defs/faixa_numerica"},
                    "largura": {"$ref": "#/$defs/faixa_numerica"},
                    "altura": {"$ref": "#/$defs/faixa_numerica"},
                },
            },
        },
    },
}


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


def main() -> None:
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


if __name__ == "__main__":
    main()
