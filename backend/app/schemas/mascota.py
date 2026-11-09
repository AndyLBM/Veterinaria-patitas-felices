
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Literal


class MascotaCreate(BaseModel):
    """
    Esquema para validar los datos
    necesarios al registrar una mascota.
    """

    # El cliente autenticado no necesita enviar este campo: el backend lo
    # obtiene de su cuenta. Para un administrador sigue siendo obligatorio.
    id_cliente: int | None = Field(default=None, gt=0)

    nombre: str = Field(
        min_length=2,
        max_length=80
    )

    especie: str = Field(
        min_length=2,
        max_length=50
    )

    raza: str | None = Field(
        default=None,
        max_length=80
    )

    sexo: Literal[
        "MACHO",
        "HEMBRA",
        "NO_ESPECIFICADO"
    ] = "NO_ESPECIFICADO"

    fecha_nacimiento: date | None = None

    peso_referencial: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=6,
        decimal_places=2
    )


class MascotaUpdate(BaseModel):
    id_cliente: int = Field(default=None, gt=0)

    nombre: str = Field(
        default=None,
        min_length=2,
        max_length=80
    )

    especie: str = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    raza: str | None = Field(
        default=None,
        max_length=80
    )

    sexo: Literal[
        "MACHO",
        "HEMBRA",
        "NO_ESPECIFICADO"
    ] = None

    fecha_nacimiento: date | None = None

    peso_referencial: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=6,
        decimal_places=2
    )
