from pydantic import BaseModel


class HistorialClinicoResponse(BaseModel):
    id_mascota: int
    atenciones: list[dict]
