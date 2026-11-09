from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.dependencies import ROL_ADMINISTRADOR, requerir_roles
from backend.app.schemas.usuario import UsuarioEstadoUpdate
from backend.app.services import usuario as usuario_service


router = APIRouter(prefix="/usuarios", tags=["Cuentas administrativas"])


@router.get("/")
def listar_usuarios(
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    return usuario_service.listar_usuarios()


@router.get("/{id_usuario}")
def obtener_usuario(
    id_usuario: int,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    cuenta = usuario_service.obtener_usuario(id_usuario)
    if cuenta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta no encontrada"
        )

    return cuenta


@router.patch("/{id_usuario}/estado")
def actualizar_estado_usuario(
    id_usuario: int,
    datos: UsuarioEstadoUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    resultado = usuario_service.actualizar_estado_usuario(id_usuario, datos.estado)
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta no encontrada"
        )

    return resultado
