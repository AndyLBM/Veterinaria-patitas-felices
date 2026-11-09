from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.cliente import ClienteCreate, ClienteUpdate
from backend.app.services import cliente as cliente_service
from backend.app.core.dependencies import (
    ROL_ADMINISTRADOR,
    requerir_roles,
    verificar_acceso_cliente,
)
from mysql.connector import IntegrityError

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registrar_cliente(datos: ClienteCreate):

    try:
        return cliente_service.registrar_cliente(datos)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado"
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/")
def listar_clientes(
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):

    clientes = cliente_service.listar_clientes()

    return clientes

@router.get("/{id_cliente}")
def obtener_cliente(
    id_cliente: int,
    usuario: dict = Depends(verificar_acceso_cliente)
):

    cliente = cliente_service.obtener_cliente(id_cliente)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado o inactivo"
        )

    return cliente

@router.put("/{id_cliente}")
def actualizar_cliente(
    id_cliente: int,
    datos: ClienteUpdate,
    usuario: dict = Depends(verificar_acceso_cliente)
):

    try:
        resultado = cliente_service.actualizar_cliente(
            id_cliente,
            datos
        )

        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado o inactivo"
            )

        return resultado

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado"
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

@router.delete("/{id_cliente}")
def desactivar_cliente(
    id_cliente: int,
    usuario: dict = Depends(verificar_acceso_cliente)
):

    resultado = cliente_service.desactivar_cliente(id_cliente)

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado o ya está inactivo"
        )

    return resultado
