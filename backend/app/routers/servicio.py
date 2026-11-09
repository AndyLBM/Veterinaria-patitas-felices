from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector import IntegrityError

from backend.app.core.dependencies import ROL_ADMINISTRADOR, requerir_roles
from backend.app.schemas.servicio import (
    ServicioCreate,
    ServicioEstadoUpdate,
    ServicioUpdate,
)
from backend.app.services import servicio as servicio_service


router = APIRouter(prefix="/servicios", tags=["Servicios"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_servicio(
    datos: ServicioCreate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        return servicio_service.registrar_servicio(datos)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un servicio con ese nombre"
        )


@router.get("/")
def listar_servicios(
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    return servicio_service.listar_servicios()


@router.get("/{id_servicio}")
def obtener_servicio(
    id_servicio: int,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    servicio = servicio_service.obtener_servicio(id_servicio)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )

    return servicio


@router.put("/{id_servicio}")
def actualizar_servicio(
    id_servicio: int,
    datos: ServicioUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        resultado = servicio_service.actualizar_servicio(id_servicio, datos)
        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return resultado
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un servicio con ese nombre"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.patch("/{id_servicio}/estado")
def actualizar_estado_servicio(
    id_servicio: int,
    datos: ServicioEstadoUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    resultado = servicio_service.actualizar_estado_servicio(
        id_servicio,
        datos.estado
    )
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )

    return resultado
