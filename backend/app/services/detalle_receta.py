from backend.app.repositories import detalle_receta as repo
def listar_detalles(id_receta):return repo.listar_detalles(id_receta)
def contexto(id_receta):return repo.obtener_contexto_receta(id_receta)
def registrar_detalle(id_receta,vet,datos):return {'id_detalle':repo.registrar_detalle(id_receta,vet,datos),'mensaje':'Detalle registrado correctamente'}
def actualizar_detalle(id_detalle,vet,datos,id_receta):repo.actualizar_detalle(id_detalle,vet,datos,id_receta);return {'id_detalle':id_detalle,'mensaje':'Detalle actualizado correctamente'}
