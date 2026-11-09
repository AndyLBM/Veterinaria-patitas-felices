from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.dependencies import obtener_veterinario_asociado, verificar_acceso_atencion
from backend.app.schemas.atencion import AtencionCreate
from backend.app.services import atencion as atencion_service


router = APIRouter(prefix="/atenciones", tags=["Atenciones clínicas"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_atencion(datos: AtencionCreate, veterinario: dict = Depends(obtener_veterinario_asociado)):
    try:
        return atencion_service.registrar_atencion(datos, veterinario["id_veterinario"])
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/{id_atencion}")
def obtener_atencion(id_atencion: int, usuario: dict = Depends(verificar_acceso_atencion)):
    atencion = atencion_service.obtener_atencion(id_atencion)
    if atencion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atención no encontrada")
    return atencion
