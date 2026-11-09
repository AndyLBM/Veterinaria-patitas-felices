from backend.app.repositories import especialidad as especialidad_repository


def registrar_especialidad(datos):
    id_especialidad = especialidad_repository.registrar_especialidad(datos)
    return {
        "mensaje": "Especialidad registrada correctamente",
        "id_especialidad": id_especialidad
    }


def listar_especialidades():
    return especialidad_repository.listar_especialidades()


def obtener_especialidad(id_especialidad: int):
    return especialidad_repository.obtener_especialidad(id_especialidad)


def actualizar_especialidad(id_especialidad: int, datos):
    especialidad = obtener_especialidad(id_especialidad)
    if especialidad is None:
        return None

    if not datos.model_dump(exclude_unset=True):
        raise ValueError("Debe proporcionar al menos un campo para actualizar")

    especialidad_repository.actualizar_especialidad(id_especialidad, datos)
    return {
        "mensaje": "Especialidad actualizada correctamente",
        "id_especialidad": id_especialidad
    }
