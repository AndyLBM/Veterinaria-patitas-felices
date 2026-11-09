from fastapi import APIRouter,Depends,HTTPException,status
from backend.app.core.dependencies import ROL_ADMINISTRADOR, obtener_usuario_actual, obtener_veterinario_asociado
from backend.app.schemas.detalle_receta import DetalleRecetaCreate,DetalleRecetaUpdate
from backend.app.services import detalle_receta as servicio
router=APIRouter(prefix='/recetas/{id_receta}/detalles',tags=['Detalles de receta'])
def err(e):raise HTTPException(status_code=403 if isinstance(e,PermissionError) else 404 if isinstance(e,LookupError) else 400,detail=str(e))
def lectura(id_receta:int,usuario:dict=Depends(obtener_usuario_actual)):
 ctx=servicio.contexto(id_receta)
 if ctx is None:raise HTTPException(status_code=404,detail='Receta no encontrada')
 if usuario['id_rol']==ROL_ADMINISTRADOR:return ctx
 vet=obtener_veterinario_asociado(usuario)
 if vet['id_veterinario']!=ctx['id_veterinario']:
  raise HTTPException(status_code=403,detail='No tienes permisos sobre esta receta')
 return ctx
@router.get('/')
def listar(id_receta:int,contexto:dict=Depends(lectura)):return servicio.listar_detalles(id_receta)
@router.post('/',status_code=status.HTTP_201_CREATED)
def crear(id_receta:int,datos:DetalleRecetaCreate,vet:dict=Depends(obtener_veterinario_asociado)):
 try:return servicio.registrar_detalle(id_receta,vet['id_veterinario'],datos)
 except (PermissionError,LookupError,ValueError) as e:err(e)
@router.put('/{id_detalle}')
def actualizar(id_receta:int,id_detalle:int,datos:DetalleRecetaUpdate,vet:dict=Depends(obtener_veterinario_asociado)):
 try:return servicio.actualizar_detalle(id_detalle,vet['id_veterinario'],datos,id_receta)
 except (PermissionError,LookupError,ValueError) as e:err(e)
