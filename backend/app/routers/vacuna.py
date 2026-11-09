from fastapi import APIRouter,Depends,HTTPException,status
from backend.app.core.dependencies import ROL_ADMINISTRADOR,ROL_CLIENTE,obtener_cliente_asociado,obtener_usuario_actual,obtener_veterinario_asociado
from backend.app.schemas.vacuna import VacunaCreate,VacunaUpdate
from backend.app.services import vacuna as servicio
router=APIRouter(prefix='/consultas/{id_consulta}/vacunas',tags=['Vacunas'])
def _lectura(id_consulta,usuario):
 ctx=servicio.contexto(id_consulta)
 if ctx is None:raise HTTPException(status_code=404,detail='Consulta no encontrada')
 if usuario['id_rol']==ROL_ADMINISTRADOR:return ctx
 if usuario['id_rol']==ROL_CLIENTE:
  if obtener_cliente_asociado(usuario)['id_cliente']!=ctx['id_cliente']:raise HTTPException(status_code=403,detail='No tienes permisos sobre esta consulta')
  return ctx
 vet=obtener_veterinario_asociado(usuario)
 if vet['id_veterinario']!=ctx['id_veterinario']:raise HTTPException(status_code=403,detail='No tienes permisos sobre esta consulta')
 return ctx
def err(e):raise HTTPException(status_code=403 if isinstance(e,PermissionError) else 404 if isinstance(e,LookupError) else 400,detail=str(e))
@router.get('/')
def listar(id_consulta:int,usuario:dict=Depends(obtener_usuario_actual)):
 _lectura(id_consulta,usuario);return servicio.listar_vacunas(id_consulta)
@router.post('/',status_code=status.HTTP_201_CREATED)
def crear(id_consulta:int,datos:VacunaCreate,vet:dict=Depends(obtener_veterinario_asociado)):
 try:return servicio.registrar_vacuna(id_consulta,vet['id_veterinario'],datos)
 except (PermissionError,LookupError,ValueError) as e:err(e)
@router.put('/{id_vacuna}')
def actualizar(id_consulta:int,id_vacuna:int,datos:VacunaUpdate,vet:dict=Depends(obtener_veterinario_asociado)):
 try:return servicio.actualizar_vacuna(id_consulta,id_vacuna,vet['id_veterinario'],datos)
 except (PermissionError,LookupError,ValueError) as e:err(e)
