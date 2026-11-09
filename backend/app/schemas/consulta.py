from pydantic import BaseModel, Field


class ConsultaCreate(BaseModel):
    diagnostico: str = Field(min_length=1)
    tratamiento: str | None = None
    observaciones: str | None = None


class ConsultaUpdate(BaseModel):
    diagnostico: str = Field(default=None, min_length=1)
    tratamiento: str | None = None
    observaciones: str | None = None
