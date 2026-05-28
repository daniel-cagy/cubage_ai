
from __future__ import annotations
from dataclasses import dataclass


FATOR_CUBAGEM = 6000


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
