from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.mascota import MascotaCreate, MascotaUpdate
from backend.app.services import mascota as mascota_service
from backend.app.core.dependencies import (
    ROL_ADMINISTRADOR,
    obtener_cliente_asociado,
    obtener_usuario_actual,
    verificar_acceso_mascota,
)

router = APIRouter(
    prefix="/mascotas",
    tags=["Mascotas"]
)


@router.get("/")
def listar_mascotas(usuario: dict = Depends(obtener_usuario_actual)):
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return mascota_service.listar_mascotas()

    cliente = obtener_cliente_asociado(usuario)
    return mascota_service.listar_mascotas_por_cliente(cliente["id_cliente"])


@router.get("/{id_mascota}")
def obtener_mascota(
    id_mascota: int,
    usuario: dict = Depends(verificar_acceso_mascota)
):
    mascota = mascota_service.obtener_mascota(id_mascota)

    if mascota is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    return mascota


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_mascota(
    datos: MascotaCreate,
    usuario: dict = Depends(obtener_usuario_actual)
):
    try:
        if usuario["id_rol"] == ROL_ADMINISTRADOR:
            if datos.id_cliente is None:
                raise ValueError(
                    "El administrador debe indicar el cliente de la mascota"
                )
            datos_registro = datos
        else:
            cliente = obtener_cliente_asociado(usuario)
            # La propiedad se determina por el usuario autenticado, nunca por
            # un identificador que provenga del navegador.
            datos_registro = datos.model_copy(
                update={"id_cliente": cliente["id_cliente"]}
            )

        return mascota_service.registrar_mascota(datos_registro)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.put("/{id_mascota}")
def actualizar_mascota(
    id_mascota: int,
    datos: MascotaUpdate,
    usuario: dict = Depends(verificar_acceso_mascota)
):

    try:
        if (
            usuario["id_rol"] != ROL_ADMINISTRADOR
            and "id_cliente" in datos.model_fields_set
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Un cliente no puede reasignar la propiedad de una mascota"
            )

        resultado = mascota_service.actualizar_mascota(
            id_mascota,
            datos
        )

        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )

        if resultado is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar la mascota"
    )

        return {
            "mensaje": "Mascota actualizada correctamente"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

@router.delete("/{id_mascota}")
def desactivar_mascota(
    id_mascota: int,
    usuario: dict = Depends(verificar_acceso_mascota)
):
    resultado = mascota_service.desactivar_mascota(id_mascota)

    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    return {"mensaje": "Mascota desactivada correctamente"}
