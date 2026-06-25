from __future__ import annotations

from product_estimator.constants import DIMENSION_KEYS, RANGE_KEYS, CONFIDENCE_LEVELS, FATOR_CUBAGEM, Objeto


def validation(output: dict) -> dict:
    erros = []
    alertas = []

    if type(output) != dict:
        erros.append("Saída deve ser um dicionário.")
        return {
            "status": False,
            "erros": erros,
            "alertas": alertas,
        }

    required_keys = {
        "produto_identificado",
        "descricao_resumida",
        "produto",
        "nivel_confianca",
    }

    missing_keys = [key for key in required_keys if key not in output]
    if missing_keys:
        erros.append(f"Saída faltando chaves obrigatórias: {', '.join(missing_keys)}.")
        return {
            "status": False,
            "erros": erros,
            "alertas": alertas,
        }

    if not is_tipagem_correta(output, erros):
        return {
            "status": False,
            "erros": erros,
            "alertas": alertas,
        }

    if output["nivel_confianca"] not in CONFIDENCE_LEVELS:
        erros.append("'nivel_confianca' deve ser 'baixo' ou 'alto'.")

    return {
        "status": len(erros) == 0,
        "erros": erros,
        "alertas": alertas,
    }


def is_tipagem_correta(output: dict, erros: list[str] | None = None) -> bool:
    if erros is None:
        erros = []

    if type(output["produto_identificado"]) != str:
        erros.append("'produto_identificado' deve ser uma string.")

    if type(output["descricao_resumida"]) != str:
        erros.append("'descricao_resumida' deve ser uma string.")

    if type(output["nivel_confianca"]) != str:
        erros.append("'nivel_confianca' deve ser uma string.")

    produto = output.get("produto")
    check_tipagem_objeto(produto, "produto", erros)

    return len(erros) == 0


def check_tipagem_objeto(objeto: dict, nome: str = "objeto", erros: list[str] | None = None) -> bool:
    if erros is None:
        erros = []

    if type(objeto) != dict:
        erros.append(f"'{nome}' deve ser um dicionário.")
        return False

    dimensoes = objeto.get("dimensoes_estimadas_cm")
    if type(dimensoes) != dict:
        erros.append(f"'{nome}.dimensoes_estimadas_cm' deve ser um dicionário.")
        return False

    for dimension_key in DIMENSION_KEYS:
        faixa = dimensoes.get(dimension_key)
        if not is_valid_numeric_range(faixa):
            erros.append(f"'{nome}.dimensoes_estimadas_cm.{dimension_key}' tem faixa numérica inválida.")

    peso = objeto.get("peso_estimado_kg")
    if not is_valid_numeric_range(peso):
        erros.append(f"'{nome}.peso_estimado_kg' tem faixa numérica inválida.")

    return len(erros) == 0


def is_valid_numeric_range(value: object) -> bool:
    if not type(value) == dict:
        return False

    if not all(key in value for key in RANGE_KEYS):
        return False

    min_value = value["min"]
    max_value = value["max"]
    estimated_value = value["estimativa"]

    if not all(is_number(item) for item in (min_value, max_value, estimated_value)):
        return False

    if min_value <= 0 or max_value <= 0 or estimated_value <= 0:
        return False

    return min_value <= estimated_value <= max_value


def is_number(value: object) -> bool:
    return type(value) in (int, float) and not type(value) == bool


def get_metricas_logisticas(produto: Objeto) -> dict[str, float]:
    metricas = {}
    volume_produto = produto.x * produto.y * produto.z
    peso_cubado = volume_produto / FATOR_CUBAGEM

    metricas["volume_produto_cm3"] = volume_produto
    metricas["densidade_produto_kg_cm3"] = produto.w / volume_produto
    metricas["peso_cubado_kg"] = peso_cubado
    metricas["peso_cobravel_estimado_kg"] = max(produto.w, peso_cubado)
    metricas["fator_cubagem"] = FATOR_CUBAGEM
    return metricas
