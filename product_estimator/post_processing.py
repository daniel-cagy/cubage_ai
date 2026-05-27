from __future__ import annotations

from dataclasses import dataclass


DIMENSION_KEYS = ("comprimento", "largura", "altura")
RANGE_KEYS = ("min", "max", "estimativa")
MEASURED_OBJECT_KEYS = ("produto", "produto_com_embalagem")
CONFIDENCE_LEVELS = {"baixo", "medio", "alto"}


@dataclass
class Objeto:
    x: int | float
    y: int | float
    z: int | float
    w: int | float

    @classmethod
    def from_dict(cls, data: dict) -> Objeto:
        return cls(
            x=data["dimensoes_estimadas_cm"]["comprimento"]["estimativa"],
            y=data["dimensoes_estimadas_cm"]["largura"]["estimativa"],
            z=data["dimensoes_estimadas_cm"]["altura"]["estimativa"],
            w=data["peso_estimado_kg"]["estimativa"],
        )

    def __ge__(self, other: "Objeto") -> bool:
        return (
            self.w >= other.w
            and self.x >= other.x
            and self.y >= other.y
            and self.z >= other.z
        )


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

    if type(output["produto_identificado"]) != str:
        erros.append("'produto_identificado' deve ser uma string.")

    if type(output["descricao_resumida"]) != str:
        erros.append("'descricao_resumida' deve ser uma string.")

    if type(output["nivel_confianca"]) != str:
        erros.append("'nivel_confianca' deve ser uma string.")

    if type(output["principais_pistas_usadas"]) != list:
        erros.append("'principais_pistas_usadas' deve ser uma lista.")

    if type(output["fatores_de_incerteza"]) != list:
        erros.append("'fatores_de_incerteza' deve ser uma lista.")

    if type(output["observacoes"]) != str:
        erros.append("'observacoes' deve ser uma string.")

    # Validar se produto sozinho tem tipagem válida
    produto = output.get("produto")
    check_tipagem_objeto(produto, "produto", erros)

    # Validar se produto com embalagem tem tipagem válida
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
    if not isinstance(value, dict):
        return False

    if not all(key in value for key in RANGE_KEYS):
        return False

    min_value = value["min"]
    max_value = value["max"]
    estimated_value = value["estimativa"]

    if not all(is_number(item) for item in (min_value, max_value, estimated_value)):
        return False

    if min_value < 0 or max_value < 0 or estimated_value < 0:
        return False

    return min_value <= estimated_value <= max_value


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
