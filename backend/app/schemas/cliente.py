
from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):

    nombre: str = Field(
        min_length=2,
        max_length=80
    )

    apellido: str = Field(
        min_length=2,
        max_length=80
    )

    correo: str = Field(
        min_length=5,
        max_length=150
    )

    password: str = Field(
        min_length=8,
        max_length=72
    )

    telefono: str | None = Field(
        default=None,
        max_length=20
    )


class ClienteUpdate(BaseModel):

    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=80
    )

    apellido: str | None = Field(
        default=None,
        min_length=2,
        max_length=80
    )

    correo: str | None = Field(
        default=None,
        min_length=5,
        max_length=150
    )

    telefono: str | None = Field(
        default=None,
        max_length=20
    )