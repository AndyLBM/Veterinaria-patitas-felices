from pydantic import BaseModel, Field


class EspecialidadCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str | None = None


class EspecialidadUpdate(BaseModel):
    nombre: str = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = None
