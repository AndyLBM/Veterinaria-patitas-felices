from backend.app.repositories import consulta as consulta_repository


def obtener_consulta(id_atencion): return consulta_repository.obtener_consulta(id_atencion)
def registrar_consulta(id_atencion,id_veterinario,datos):
    return {"mensaje":"Consulta registrada correctamente","id_consulta":consulta_repository.registrar_consulta(id_atencion,id_veterinario,datos)}
def actualizar_consulta(id_atencion,id_veterinario,datos):
    consulta_repository.actualizar_consulta(id_atencion,id_veterinario,datos)
    return {"mensaje":"Consulta actualizada correctamente","id_atencion":id_atencion}
