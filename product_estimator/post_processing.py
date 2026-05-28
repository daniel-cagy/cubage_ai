from __future__ import annotations

from dataclasses import dataclass
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
        "produto_com_embalagem",
        "nivel_confianca",
        "principais_pistas_usadas",
        "fatores_de_incerteza",
        "observacoes",
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
        erros.append("'nivel_confianca' deve ser 'baixo', 'medio' ou 'alto'.")

    if len(output["principais_pistas_usadas"]) == 0:
        alertas.append("'principais_pistas_usadas' está vazio.")

    if output["nivel_confianca"] == "baixo" and len(output["fatores_de_incerteza"]) == 0:
        alertas.append("Confiança baixa sem fatores de incerteza informados.")

    if erros:
        return {
            "status": False,
            "erros": erros,
            "alertas": alertas,
        }

    produto = Objeto.from_dict(output["produto"])
    produto_com_embalagem = Objeto.from_dict(output["produto_com_embalagem"])
    if not (produto_com_embalagem >= produto):
        erros.append("Produto não pode ser maior que o produto com embalagem.")

    if produto_com_embalagem == produto:
        alertas.append("Produto com embalagem tem as mesmas dimensões e peso do produto.")

    return {
        "status": len(erros) == 0,
        "erros": erros,
        "alertas": alertas,
    }


def is_tipagem_correta(output: dict, erros: list[str] | None = None) -> bool:
    if erros is None:
        erros = []

    produto = output.get("produto")
    check_tipagem_objeto(produto, "produto", erros)

    produto_com_embalagem = output.get("produto_com_embalagem")
    check_tipagem_objeto(produto_com_embalagem, "produto_com_embalagem", erros)

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


def get_metricas_logisticas(produto: Objeto, produto_com_embalagem: Objeto) -> dict[str, float]:
    metricas = {}
    volume_produto = produto.x * produto.y * produto.z
    volume_embalagem = produto_com_embalagem.x * produto_com_embalagem.y * produto_com_embalagem.z
    metricas["densidade_produto"] = produto.w / volume_produto
    metricas["densidade_embalagem"] = produto_com_embalagem.w / volume_embalagem
    metricas["fator_cubagem_produto"] = volume_produto / FATOR_CUBAGEM
    metricas["fator_cubagem_embalagem"] = volume_embalagem / FATOR_CUBAGEM
    return metricas

def get_incerteza_calculada(produto: dict, produto_com_embalagem: dict) -> dict[str, float]:
    incertezas = {}

    dimensoes_produto = produto["dimensoes_estimadas_cm"]
    
    comprimento_produto = dimensoes_produto["comprimento"]
    altura_produto = dimensoes_produto["altura"]
    largura_produto = dimensoes_produto["largura"]
    peso_produto = produto["peso_estimado_kg"]
    
    incertezas["comprimento"] = calcula_incerteza_no_valor(comprimento_produto)
    incertezas["altura"] = calcula_incerteza_no_valor(altura_produto)
    incertezas["largura"] = calcula_incerteza_no_valor(largura_produto)
    incertezas["peso"] = calcula_incerteza_no_valor(peso_produto)


    dimensoes_embalagem = produto_com_embalagem["dimensoes_estimadas_cm"]

    dimensoes_embalagem = produto_com_embalagem["dimensoes_estimadas_cm"]
    comprimento_embalagem = dimensoes_embalagem["comprimento"]
    altura_embalagem = dimensoes_embalagem["altura"]
    largura_embalagem = dimensoes_embalagem["largura"]
    peso_embalagem = produto_com_embalagem["peso_estimado_kg"]
    
    incertezas["comprimento_embalagem"] = calcula_incerteza_no_valor(comprimento_embalagem)
    incertezas["altura_embalagem"] = calcula_incerteza_no_valor(altura_embalagem)
    incertezas["largura_embalagem"] = calcula_incerteza_no_valor(largura_embalagem)
    incertezas["peso_embalagem"] = calcula_incerteza_no_valor(peso_embalagem)

    return incertezas


def calcula_incerteza_no_valor(faixa: dict) -> float:
    min_value = faixa["min"]
    max_value = faixa["max"]
    estimated_value = faixa["estimativa"]
    if estimated_value == 0:
        return 0.0
    return (max_value - min_value) / estimated_value



