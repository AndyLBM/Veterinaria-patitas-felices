from fastapi import APIRouter, HTTPException, status, Depends

from backend.app.schemas.auth import LoginRequest
from backend.app.services import auth as auth_service
from backend.app.core.dependencies import (
    obtener_usuario_actual,
    requerir_roles
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login")
def iniciar_sesion(datos: LoginRequest):
    resultado = auth_service.iniciar_sesion(datos)

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    return resultado


@router.get("/me")
def obtener_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    return usuario


@router.get("/admin")
def acceso_administrador(
    usuario: dict = Depends(requerir_roles(1))
):
    return {
        "mensaje": "Acceso autorizado para administrador",
        "usuario": usuario
    }