from backend.app.repositories import receta as repo
def listar_recetas(id_consulta):return repo.listar_recetas(id_consulta)
def contexto(id_consulta):return repo.obtener_contexto_consulta(id_consulta)
def registrar_receta(id_consulta,vet,datos):return {'id_receta':repo.registrar_receta(id_consulta,vet,datos),'mensaje':'Receta registrada correctamente'}
def actualizar_receta(id_receta,vet,datos,id_consulta):repo.actualizar_receta(id_receta,vet,datos,id_consulta);return {'id_receta':id_receta,'mensaje':'Receta actualizada correctamente'}
