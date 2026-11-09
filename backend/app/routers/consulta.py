from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.core.dependencies import obtener_veterinario_asociado, verificar_acceso_atencion
from backend.app.schemas.consulta import ConsultaCreate, ConsultaUpdate
from backend.app.services import consulta as servicio

router=APIRouter(prefix="/atenciones/{id_atencion}/consulta",tags=["Consultas clínicas"])
def _error(error):
    codigo=403 if isinstance(error,PermissionError) else 404 if isinstance(error,LookupError) else 400
    raise HTTPException(status_code=codigo,detail=str(error))
@router.get("/")
def obtener(id_atencion:int, usuario:dict=Depends(verificar_acceso_atencion)):
    dato=servicio.obtener_consulta(id_atencion)
    if dato is None: raise HTTPException(status_code=404,detail="Consulta no encontrada")
    return dato
@router.post("/",status_code=status.HTTP_201_CREATED)
def registrar(id_atencion:int,datos:ConsultaCreate,veterinario:dict=Depends(obtener_veterinario_asociado)):
    try: return servicio.registrar_consulta(id_atencion,veterinario["id_veterinario"],datos)
    except (PermissionError,LookupError,ValueError) as error: _error(error)
@router.put("/")
def actualizar(id_atencion:int,datos:ConsultaUpdate,veterinario:dict=Depends(obtener_veterinario_asociado)):
    try: return servicio.actualizar_consulta(id_atencion,veterinario["id_veterinario"],datos)
    except (PermissionError,LookupError,ValueError) as error: _error(error)
