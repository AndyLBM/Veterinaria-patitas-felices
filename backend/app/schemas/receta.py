from pydantic import BaseModel


class RecetaCreate(BaseModel):
    indicaciones: str | None = None


class RecetaUpdate(RecetaCreate):
    pass
