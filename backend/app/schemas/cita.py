from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from backend.app.core.fechas import fecha_local_lima


EstadoCita = Literal[
    "PROGRAMADA",
    "CONFIRMADA",
    "EN_ATENCION",
    "ATENDIDA",
    "CANCELADA",
    "NO_ASISTIO",
]


class CitaCreate(BaseModel):
    id_mascota: int = Field(gt=0)
    id_veterinario: int = Field(gt=0)
    id_servicio: int = Field(gt=0)
    fecha_inicio: datetime
    motivo: str | None = None

    @field_validator("fecha_inicio")
    @classmethod
    def normalizar_fecha(cls, valor: datetime) -> datetime:
        return fecha_local_lima(valor)


class CitaReprogramacion(BaseModel):
    id_veterinario: int = Field(gt=0)
    fecha_inicio: datetime

    @field_validator("fecha_inicio")
    @classmethod
    def normalizar_fecha(cls, valor: datetime) -> datetime:
        return fecha_local_lima(valor)


class CitaEstadoUpdate(BaseModel):
    estado: EstadoCita


class CitaAgendaResponse(BaseModel):
    id_cita: int
    id_mascota: int
    nombre_mascota: str
    especie_mascota: str
    id_servicio: int
    nombre_servicio: str
    fecha_inicio: datetime
    fecha_fin: datetime
    duracion_minutos: int
    estado: EstadoCita
    motivo: str | None
    id_cliente: int
    nombre_cliente: str
    apellido_cliente: str
    telefono_cliente: str | None
