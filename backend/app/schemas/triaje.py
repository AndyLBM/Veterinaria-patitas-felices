from decimal import Decimal

from pydantic import BaseModel, Field


class TriajeCreate(BaseModel):
    peso: Decimal | None = Field(default=None, gt=0, max_digits=6, decimal_places=2)
    temperatura: Decimal | None = Field(default=None, gt=0, max_digits=4, decimal_places=1)
    frecuencia_cardiaca: int | None = Field(default=None, gt=0)
    frecuencia_respiratoria: int | None = Field(default=None, gt=0)
    observaciones: str | None = None


class TriajeUpdate(TriajeCreate):
    pass
