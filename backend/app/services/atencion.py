from backend.app.repositories import atencion as atencion_repository


def registrar_atencion(datos, id_veterinario: int):
    id_atencion = atencion_repository.registrar_atencion_segura(
        datos.id_cita, id_veterinario, datos.observaciones
    )
    return {"mensaje": "Atención registrada correctamente", "id_atencion": id_atencion}


def obtener_atencion(id_atencion: int):
    return atencion_repository.obtener_atencion(id_atencion)


def obtener_atencion_por_cita(id_cita: int):
    return atencion_repository.obtener_atencion_por_cita(id_cita)
