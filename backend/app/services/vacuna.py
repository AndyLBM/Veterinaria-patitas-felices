from backend.app.repositories import vacuna as repo
def listar_vacunas(i):return repo.listar_vacunas(i)
def contexto(i):return repo.obtener_contexto_consulta(i)
def registrar_vacuna(i,v,d):return {'id_vacuna':repo.registrar_vacuna(i,v,d),'mensaje':'Vacuna registrada correctamente'}
def actualizar_vacuna(i,x,v,d):repo.actualizar_vacuna(i,x,v,d);return {'id_vacuna':x,'mensaje':'Vacuna actualizada correctamente'}
