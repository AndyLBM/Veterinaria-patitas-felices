from fastapi import APIRouter,Depends,HTTPException,status
from backend.app.core.dependencies import ROL_ADMINISTRADOR, obtener_usuario_actual, obtener_veterinario_asociado
from backend.app.schemas.receta import RecetaCreate,RecetaUpdate
from backend.app.services import receta as servicio
router=APIRouter(prefix='/consultas/{id_consulta}/recetas',tags=['Recetas'])
def err(e):raise HTTPException(status_code=403 if isinstance(e,PermissionError) else 404 if isinstance(e,LookupError) else 400,detail=str(e))
def lectura(id_consulta:int,usuario:dict=Depends(obtener_usuario_actual)):
 ctx=servicio.contexto(id_consulta)
 if ctx is None:raise HTTPException(status_code=404,detail='Consulta no encontrada')
 if usuario['id_rol']==ROL_ADMINISTRADOR:return ctx
 vet=obtener_veterinario_asociado(usuario)
 if vet['id_veterinario']!=ctx['id_veterinario']:
  raise HTTPException(status_code=403,detail='No tienes permisos sobre esta consulta')
 return ctx
@router.get('/')
def listar(id_consulta:int,contexto:dict=Depends(lectura)):return servicio.listar_recetas(id_consulta)
@router.post('/',status_code=status.HTTP_201_CREATED)
def crear(id_consulta:int,datos:RecetaCreate,vet:dict=Depends(obtener_veterinario_asociado)):
 try:return servicio.registrar_receta(id_consulta,vet['id_veterinario'],datos)
 except (PermissionError,LookupError,ValueError) as e:err(e)
@router.put('/{id_receta}')
def actualizar(id_consulta:int,id_receta:int,datos:RecetaUpdate,vet:dict=Depends(obtener_veterinario_asociado)):
 try:return servicio.actualizar_receta(id_receta,vet['id_veterinario'],datos,id_consulta)
 except (PermissionError,LookupError,ValueError) as e:err(e)
