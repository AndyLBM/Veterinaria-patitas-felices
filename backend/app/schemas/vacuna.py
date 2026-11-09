from datetime import date
from pydantic import BaseModel, Field, model_validator

class VacunaCreate(BaseModel):
    nombre_vacuna: str = Field(min_length=1, max_length=150)
    fecha_aplicacion: date
    proxima_dosis: date | None = None
    observaciones: str | None = None
    @model_validator(mode='after')
    def validar_fechas(self):
        if self.proxima_dosis is not None and self.proxima_dosis < self.fecha_aplicacion: raise ValueError('La próxima dosis no puede ser anterior a la aplicación')
        return self

class VacunaUpdate(VacunaCreate):
    pass
