from backend.app.repositories import triaje as triaje_repository


def obtener_triaje(id_atencion): return triaje_repository.obtener_triaje(id_atencion)
def registrar_triaje(id_atencion,id_veterinario,datos):
    return {"mensaje":"Triaje registrado correctamente","id_triaje":triaje_repository.registrar_triaje(id_atencion,id_veterinario,datos)}
def actualizar_triaje(id_atencion,id_veterinario,datos):
    triaje_repository.actualizar_triaje(id_atencion,id_veterinario,datos)
    return {"mensaje":"Triaje actualizado correctamente","id_atencion":id_atencion}
