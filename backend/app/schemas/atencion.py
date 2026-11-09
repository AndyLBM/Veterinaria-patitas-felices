from pydantic import BaseModel, Field


class AtencionCreate(BaseModel):
    id_cita: int = Field(gt=0)
    observaciones: str | None = None
