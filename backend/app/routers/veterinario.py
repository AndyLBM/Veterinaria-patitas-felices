from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector import IntegrityError

from backend.app.core.dependencies import ROL_ADMINISTRADOR, requerir_roles
from backend.app.schemas.usuario import UsuarioEstadoUpdate
from backend.app.schemas.veterinario import VeterinarioCreate, VeterinarioUpdate
from backend.app.services import veterinario as veterinario_service


router = APIRouter(prefix="/veterinarios", tags=["Veterinarios"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_veterinario(
    datos: VeterinarioCreate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        return veterinario_service.registrar_veterinario(datos)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo o número de colegiatura ya está registrado"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/")
def listar_veterinarios(
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    return veterinario_service.listar_veterinarios()


@router.get("/{id_veterinario}")
def obtener_veterinario(
    id_veterinario: int,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    veterinario = veterinario_service.obtener_veterinario(id_veterinario)
    if veterinario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )

    return veterinario


@router.put("/{id_veterinario}")
def actualizar_veterinario(
    id_veterinario: int,
    datos: VeterinarioUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        resultado = veterinario_service.actualizar_veterinario(
            id_veterinario,
            datos
        )
        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return resultado
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo o número de colegiatura ya está registrado"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.patch("/{id_veterinario}/estado")
def actualizar_estado_veterinario(
    id_veterinario: int,
    datos: UsuarioEstadoUpdate,
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    resultado = veterinario_service.actualizar_estado_veterinario(
        id_veterinario,
        datos.estado
    )
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )

    return resultado
