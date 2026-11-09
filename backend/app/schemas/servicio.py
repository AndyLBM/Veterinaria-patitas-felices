from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class ServicioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str | None = None
    duracion_minutos: int = Field(gt=0)
    precio: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )


class ServicioUpdate(BaseModel):
    nombre: str = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = None
    duracion_minutos: int = Field(default=None, gt=0)
    precio: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )


class ServicioEstadoUpdate(BaseModel):
    estado: Literal["ACTIVO", "INACTIVO"]
