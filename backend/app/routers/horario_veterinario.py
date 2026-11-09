from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.core.dependencies import ROL_ADMINISTRADOR, requerir_roles
from backend.app.schemas.horario_veterinario import (
    HorarioVeterinarioCreate,
    HorarioVeterinarioUpdate,
)
from backend.app.services import horario_veterinario as horario_service


router = APIRouter(
    prefix="/horarios-veterinarios",
    tags=["Horarios de veterinarios"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_horario(
    datos: HorarioVeterinarioCreate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        return horario_service.registrar_horario(datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/")
def listar_horarios(
    id_veterinario: int | None = Query(default=None, gt=0),
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    return horario_service.listar_horarios(id_veterinario)


@router.get("/{id_horario}")
def obtener_horario(
    id_horario: int,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    horario = horario_service.obtener_horario(id_horario)
    if horario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado"
        )

    return horario


@router.put("/{id_horario}")
def actualizar_horario(
    id_horario: int,
    datos: HorarioVeterinarioUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        resultado = horario_service.actualizar_horario(id_horario, datos)
        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Horario no encontrado"
            )

        return resultado
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
