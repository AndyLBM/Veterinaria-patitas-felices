from datetime import time, timedelta

from pydantic import BaseModel, Field, model_validator


def segundos_desde_medianoche(valor: time | timedelta) -> float:
    if isinstance(valor, timedelta):
        return valor.total_seconds()

    return (
        valor.hour * 3600
        + valor.minute * 60
        + valor.second
        + valor.microsecond / 1_000_000
    )


class HorarioVeterinarioCreate(BaseModel):
    id_veterinario: int = Field(gt=0)
    dia_semana: int = Field(ge=1, le=7)
    hora_inicio: time
    hora_fin: time

    @model_validator(mode="after")
    def validar_rango_horario(self):
        if segundos_desde_medianoche(self.hora_inicio) >= segundos_desde_medianoche(
            self.hora_fin
        ):
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        return self


class HorarioVeterinarioUpdate(BaseModel):
    dia_semana: int = Field(default=None, ge=1, le=7)
    hora_inicio: time | None = None
    hora_fin: time | None = None

    @model_validator(mode="after")
    def validar_rango_horario(self):
        if (
            self.hora_inicio is not None
            and self.hora_fin is not None
            and segundos_desde_medianoche(self.hora_inicio)
            >= segundos_desde_medianoche(self.hora_fin)
        ):
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        return self
