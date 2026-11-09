from pydantic import BaseModel, Field


class VeterinarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    correo: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=72)
    telefono: str | None = Field(default=None, max_length=20)
    id_especialidad: int = Field(gt=0)
    numero_colegiatura: str = Field(min_length=2, max_length=50)


class VeterinarioUpdate(BaseModel):
    nombre: str = Field(default=None, min_length=2, max_length=80)
    apellido: str = Field(default=None, min_length=2, max_length=80)
    correo: str = Field(default=None, min_length=5, max_length=150)
    telefono: str | None = Field(default=None, max_length=20)
    id_especialidad: int = Field(default=None, gt=0)
    numero_colegiatura: str = Field(default=None, min_length=2, max_length=50)
