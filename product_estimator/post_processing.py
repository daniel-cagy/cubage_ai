from __future__ import annotations

from copy import deepcopy
from math import ceil, floor
from typing import Any

from product_estimator.constants import (
    DIMENSION_INTERVAL_CALIBRATION,
    DIMENSION_DISPLAY_DECIMAL_PLACES,
    DIMENSION_INTERVAL_CALIBRATION_MULTIPLIER,
    DIMENSION_KEYS,
    RANGE_KEYS,
    FATOR_CUBAGEM,
    MIN_DIMENSION_DISPLAY_VALUE_CM,
    MIN_DIMENSION_RANGE_VALUE_CM,
    MIN_WEIGHT_RANGE_VALUE_KG,
    Objeto,
    WEIGHT_DISPLAY_DECIMAL_PLACES,
    WEIGHT_INTERVAL_CALIBRATION,
    WEIGHT_INTERVAL_CALIBRATION_MULTIPLIER,
    MIN_WEIGHT_DISPLAY_VALUE_KG,
)


def apply_calibrated_intervals(output: dict, known_measures: dict[str, float] | None = None) -> dict:
    calibrated_output = deepcopy(output)
    produto = calibrated_output.get("produto", {})
    dimensoes = produto.get("dimensoes_estimadas_cm", {})

    for dimension_key in DIMENSION_KEYS:
        range_data = dimensoes.get(dimension_key, {})
        estimate = range_data.get("estimativa")
        calibration = DIMENSION_INTERVAL_CALIBRATION[dimension_key]
        dimensoes[dimension_key] = build_calibrated_range(
            estimate=estimate,
            bias=calibration["bias"],
            std=calibration["std"],
            min_allowed_value=MIN_DIMENSION_RANGE_VALUE_CM,
            multiplier=DIMENSION_INTERVAL_CALIBRATION_MULTIPLIER,
        )

    peso = produto.get("peso_estimado_kg", {})
    weight_estimate = peso.get("estimativa")
    weight_calibration = get_weight_interval_calibration(weight_estimate)
    produto["peso_estimado_kg"] = build_calibrated_range(
        estimate=weight_estimate,
        bias=weight_calibration["bias"],
        std=weight_calibration["std"],
        min_allowed_value=MIN_WEIGHT_RANGE_VALUE_KG,
        multiplier=WEIGHT_INTERVAL_CALIBRATION_MULTIPLIER,
    )

    round_output_ranges(calibrated_output)
    apply_known_measures(calibrated_output, known_measures)

    return calibrated_output


def apply_known_measures(output: dict, known_measures: dict[str, float] | None) -> None:
    if not known_measures:
        return

    produto = output.get("produto", {})
    dimensoes = produto.get("dimensoes_estimadas_cm", {})

    for measure_type, known_value in known_measures.items():
        if not is_number(known_value) or known_value <= 0:
            continue

        if measure_type in DIMENSION_KEYS:
            apply_exact_value_range(dimensoes.get(measure_type, {}), known_value)
        elif measure_type == "peso":
            apply_exact_value_range(produto.get("peso_estimado_kg", {}), known_value)


def apply_exact_value_range(faixa: dict, value: int | float) -> None:
    if type(faixa) != dict:
        return

    faixa["min"] = value
    faixa["max"] = value
    faixa["estimativa"] = value


def round_output_ranges(output: dict) -> None:
    produto = output.get("produto", {})
    dimensoes = produto.get("dimensoes_estimadas_cm", {})

    for dimension_key in DIMENSION_KEYS:
        faixa = dimensoes.get(dimension_key, {})
        round_dimension_range(faixa)

    round_weight_range(produto.get("peso_estimado_kg", {}))


def round_dimension_range(faixa: dict) -> None:
    if not is_valid_range_for_rounding(faixa):
        return

    min_value = max(MIN_DIMENSION_DISPLAY_VALUE_CM, floor(faixa["min"]))
    max_value = max(min_value, ceil(faixa["max"]))
    estimate = round(faixa["estimativa"], DIMENSION_DISPLAY_DECIMAL_PLACES)
    estimate = min(max(estimate, min_value), max_value)

    faixa["min"] = min_value
    faixa["max"] = max_value
    faixa["estimativa"] = estimate


def round_weight_range(faixa: dict) -> None:
    if not is_valid_range_for_rounding(faixa):
        return

    decimal_factor = 10 ** WEIGHT_DISPLAY_DECIMAL_PLACES
    min_value = floor(faixa["min"] * decimal_factor) / decimal_factor
    min_value = max(MIN_WEIGHT_DISPLAY_VALUE_KG, min_value)
    max_value = ceil(faixa["max"] * decimal_factor) / decimal_factor
    max_value = max(min_value, max_value)
    estimate = round(faixa["estimativa"], WEIGHT_DISPLAY_DECIMAL_PLACES)
    estimate = min(max(estimate, min_value), max_value)

    faixa["min"] = round(min_value, WEIGHT_DISPLAY_DECIMAL_PLACES)
    faixa["max"] = round(max_value, WEIGHT_DISPLAY_DECIMAL_PLACES)
    faixa["estimativa"] = round(estimate, WEIGHT_DISPLAY_DECIMAL_PLACES)


def is_valid_range_for_rounding(faixa: object) -> bool:
    if type(faixa) != dict:
        return False

    if not all(key in faixa for key in RANGE_KEYS):
        return False

    return all(is_number(faixa[key]) for key in RANGE_KEYS)


def build_calibrated_range(
    estimate: Any,
    bias: int | float,
    std: int | float,
    min_allowed_value: int | float,
    multiplier: int | float,
) -> dict[str, Any]:
    if not is_number(estimate):
        return {"min": estimate, "max": estimate, "estimativa": estimate}

    estimate = max(float(estimate), float(min_allowed_value))
    center = estimate - float(bias)
    margin = float(multiplier) * float(std)

    min_value = max(float(min_allowed_value), center - margin)
    max_value = max(center + margin, estimate)

    if min_value > estimate:
        min_value = estimate
    if max_value < estimate:
        max_value = estimate

    return {
        "min": round(min_value, 4),
        "max": round(max_value, 4),
        "estimativa": round(estimate, 4),
    }


def get_weight_interval_calibration(estimate: Any) -> dict[str, Any]:
    if not is_number(estimate):
        return WEIGHT_INTERVAL_CALIBRATION[0]

    estimate = float(estimate)
    for calibration in WEIGHT_INTERVAL_CALIBRATION:
        max_estimate = calibration["max_estimate_kg"]
        if max_estimate is None or estimate < max_estimate:
            return calibration

    return WEIGHT_INTERVAL_CALIBRATION[-1]


def get_interval_calibration_info(output: dict) -> dict[str, Any]:
    produto = output.get("produto", {})
    peso = produto.get("peso_estimado_kg", {})
    weight_calibration = get_weight_interval_calibration(peso.get("estimativa"))

    return {
        "metodo": "desvio_padrao_pos_processamento",
        "multiplicadores_desvio_padrao": {
            "dimensoes": DIMENSION_INTERVAL_CALIBRATION_MULTIPLIER,
            "peso": WEIGHT_INTERVAL_CALIBRATION_MULTIPLIER,
        },
        "dimensoes": DIMENSION_INTERVAL_CALIBRATION,
        "peso": {
            "classe_por_estimativa": weight_calibration["class"],
            "bias": weight_calibration["bias"],
            "std": weight_calibration["std"],
        },
    }


def validation(output: dict, known_measures: dict[str, float] | None = None) -> dict:
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

    if known_measures:
        check_medidas_conhecidas(output, known_measures, alertas)

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

    produto = output.get("produto")
    check_tipagem_objeto(produto, "produto", erros)

    return len(erros) == 0


def check_medidas_conhecidas(output: dict, known_measures: dict[str, float], alertas: list[str]) -> None:
    produto = output["produto"]
    dimensoes = produto["dimensoes_estimadas_cm"]

    for measure_type, known_value in known_measures.items():
        if measure_type in DIMENSION_KEYS:
            faixa = dimensoes[measure_type]
            unit = "cm"
        elif measure_type == "peso":
            faixa = produto["peso_estimado_kg"]
            unit = "kg"
        else:
            continue

        if known_value < faixa["min"] or known_value > faixa["max"]:
            alertas.append(
                f"Medida conhecida de {measure_type} ({known_value:g} {unit}) ficou fora da faixa estimada."
            )
            continue

        if abs(faixa["estimativa"] - known_value) / known_value > 0.1:
            alertas.append(
                f"Estimativa de {measure_type} ficou distante da medida conhecida ({known_value:g} {unit})."
            )


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


def get_metricas_logisticas(produto: Objeto, fator_cubagem: int | float = FATOR_CUBAGEM) -> dict[str, float]:
    metricas = {}
    volume_produto = produto.x * produto.y * produto.z
    peso_cubado = volume_produto / fator_cubagem

    metricas["volume_produto_cm3"] = volume_produto
    metricas["densidade_produto_kg_cm3"] = produto.w / volume_produto
    metricas["peso_cubado_kg"] = peso_cubado
    metricas["peso_cobravel_estimado_kg"] = max(produto.w, peso_cubado)
    metricas["fator_cubagem"] = fator_cubagem
    return metricas


def get_produto_ajustado(output: dict, corrections: dict[str, float]) -> dict:
    produto = output["produto"]
    dimensoes = produto["dimensoes_estimadas_cm"]

    return {
        "dimensoes_cm": {
            "comprimento": corrections.get("comprimento", dimensoes["comprimento"]["estimativa"]),
            "largura": corrections.get("largura", dimensoes["largura"]["estimativa"]),
            "altura": corrections.get("altura", dimensoes["altura"]["estimativa"]),
        },
        "peso_kg": corrections.get("peso", produto["peso_estimado_kg"]["estimativa"]),
        "campos_corrigidos": sorted(corrections.keys()),
    }


def get_objeto_ajustado(output: dict, corrections: dict[str, float]) -> Objeto:
    produto_ajustado = get_produto_ajustado(output, corrections)
    dimensoes = produto_ajustado["dimensoes_cm"]

    return Objeto(
        x=dimensoes["comprimento"],
        y=dimensoes["largura"],
        z=dimensoes["altura"],
        w=produto_ajustado["peso_kg"],
    )

