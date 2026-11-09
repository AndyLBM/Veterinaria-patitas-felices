from pydantic import BaseModel, Field


class DetalleRecetaCreate(BaseModel):
    medicamento: str = Field(min_length=1, max_length=150)
    dosis: str = Field(min_length=1, max_length=100)
    frecuencia: str | None = Field(default=None, max_length=100)
    duracion: str | None = Field(default=None, max_length=100)
    indicaciones: str | None = None


class DetalleRecetaUpdate(DetalleRecetaCreate):
    pass
