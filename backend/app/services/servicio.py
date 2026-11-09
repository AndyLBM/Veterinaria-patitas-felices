from backend.app.repositories import servicio as servicio_repository


def registrar_servicio(datos):
    id_servicio = servicio_repository.registrar_servicio(datos)
    return {
        "mensaje": "Servicio registrado correctamente",
        "id_servicio": id_servicio
    }


def listar_servicios():
    return servicio_repository.listar_servicios()


def obtener_servicio(id_servicio: int):
    return servicio_repository.obtener_servicio(id_servicio)


def actualizar_servicio(id_servicio: int, datos):
    servicio = obtener_servicio(id_servicio)
    if servicio is None:
        return None

    if not datos.model_dump(exclude_unset=True):
        raise ValueError("Debe proporcionar al menos un campo para actualizar")

    servicio_repository.actualizar_servicio(id_servicio, datos)
    return {
        "mensaje": "Servicio actualizado correctamente",
        "id_servicio": id_servicio
    }


def actualizar_estado_servicio(id_servicio: int, estado: str):
    servicio = obtener_servicio(id_servicio)
    if servicio is None:
        return None

    servicio_repository.actualizar_estado_servicio(id_servicio, estado)
    return {
        "mensaje": "Estado del servicio actualizado correctamente",
        "id_servicio": id_servicio,
        "estado": estado
    }
