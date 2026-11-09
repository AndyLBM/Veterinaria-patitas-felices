from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    correo: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=1, max_length=72)