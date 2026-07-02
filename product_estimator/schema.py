from typing import Any


MEASUREMENT_SCHEMA: dict[str, Any] = {
    "name": "estimativa_dimensional_produto",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "produto_identificado",
            "descricao_resumida",
            "produto",
        ],
        "properties": {
            "produto_identificado": {"type": "string"},
            "descricao_resumida": {"type": "string"},
            "produto": {"$ref": "#/$defs/medidas_e_peso"},
        },
        "$defs": {
            "estimativa_numerica": {
                "type": "object",
                "additionalProperties": False,
                "required": ["estimativa"],
                "properties": {
                    "estimativa": {"type": "number", "minimum": 0},
                },
            },
            "dimensoes": {
                "type": "object",
                "additionalProperties": False,
                "required": ["comprimento", "largura", "altura"],
                "properties": {
                    "comprimento": {"$ref": "#/$defs/estimativa_numerica"},
                    "largura": {"$ref": "#/$defs/estimativa_numerica"},
                    "altura": {"$ref": "#/$defs/estimativa_numerica"},
                },
            },
            "medidas_e_peso": {
                "type": "object",
                "additionalProperties": False,
                "required": ["dimensoes_estimadas_cm", "peso_estimado_kg"],
                "properties": {
                    "dimensoes_estimadas_cm": {"$ref": "#/$defs/dimensoes"},
                    "peso_estimado_kg": {"$ref": "#/$defs/estimativa_numerica"},
                },
            },
        },
    },
}
