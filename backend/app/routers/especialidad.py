from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector import IntegrityError

from backend.app.core.dependencies import ROL_ADMINISTRADOR, requerir_roles
from backend.app.schemas.especialidad import EspecialidadCreate, EspecialidadUpdate
from backend.app.services import especialidad as especialidad_service


router = APIRouter(prefix="/especialidades", tags=["Especialidades"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_especialidad(
    datos: EspecialidadCreate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        return especialidad_service.registrar_especialidad(datos)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una especialidad con ese nombre"
        )


@router.get("/")
def listar_especialidades(
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    return especialidad_service.listar_especialidades()


@router.get("/{id_especialidad}")
def obtener_especialidad(
    id_especialidad: int,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    especialidad = especialidad_service.obtener_especialidad(id_especialidad)
    if especialidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Especialidad no encontrada"
        )

    return especialidad


@router.put("/{id_especialidad}")
def actualizar_especialidad(
    id_especialidad: int,
    datos: EspecialidadUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        resultado = especialidad_service.actualizar_especialidad(
            id_especialidad,
            datos
        )
        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Especialidad no encontrada"
            )

        return resultado
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una especialidad con ese nombre"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
