from fastapi import APIRouter,Depends,HTTPException
from backend.app.core.dependencies import ROL_ADMINISTRADOR,ROL_CLIENTE,obtener_cliente_asociado,obtener_usuario_actual,obtener_veterinario_asociado
from backend.app.services import historial_clinico as servicio
router=APIRouter(prefix='/mascotas/{id_mascota}/historial-clinico',tags=['Historial clínico'])
def acceso(id_mascota,usuario):
 m=servicio.contexto(id_mascota)
 if m is None:raise HTTPException(status_code=404,detail='Mascota no encontrada')
 if usuario['id_rol']==ROL_ADMINISTRADOR:return m
 if usuario['id_rol']==ROL_CLIENTE:
  if obtener_cliente_asociado(usuario)['id_cliente']!=m['id_cliente']:raise HTTPException(status_code=403,detail='No tienes permisos sobre esta mascota')
  return m
 v=obtener_veterinario_asociado(usuario)
 if not servicio.veterinario_autorizado(id_mascota,v['id_veterinario']):raise HTTPException(status_code=403,detail='No tienes una cita asignada para esta mascota')
 return m
@router.get('/')
def historial(id_mascota:int,usuario:dict=Depends(obtener_usuario_actual)):
 m=acceso(id_mascota,usuario);return {'mascota':m,'atenciones':servicio.obtener(id_mascota)}
@router.get('/{id_atencion}')
def detalle(id_mascota:int,id_atencion:int,usuario:dict=Depends(obtener_usuario_actual)):
 m=acceso(id_mascota,usuario);a=servicio.obtener(id_mascota,id_atencion)
 if not a:raise HTTPException(status_code=404,detail='Atención no encontrada para esta mascota')
 return {'mascota':m,'atencion':a[0]}
