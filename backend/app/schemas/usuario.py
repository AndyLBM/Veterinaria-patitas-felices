from typing import Literal

from pydantic import BaseModel


class UsuarioEstadoUpdate(BaseModel):
    estado: Literal["ACTIVO", "INACTIVO"]
