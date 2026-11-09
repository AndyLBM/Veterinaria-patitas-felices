import bcrypt

from backend.app.repositories import especialidad as especialidad_repository
from backend.app.repositories import veterinario as veterinario_repository


def _generar_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("La contraseña no puede superar los 72 bytes")

    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def _validar_especialidad(id_especialidad: int):
    if especialidad_repository.obtener_especialidad(id_especialidad) is None:
        raise ValueError("La especialidad indicada no existe")


def registrar_veterinario(datos):
    _validar_especialidad(datos.id_especialidad)
    password_hash = _generar_password_hash(datos.password)
    resultado = veterinario_repository.registrar_veterinario(datos, password_hash)

    return {
        "mensaje": "Veterinario registrado correctamente",
        "id_veterinario": resultado["id_veterinario"],
        "id_usuario": resultado["id_usuario"]
    }


def listar_veterinarios():
    return veterinario_repository.listar_veterinarios()


def obtener_veterinario(id_veterinario: int):
    return veterinario_repository.obtener_veterinario(id_veterinario)


def actualizar_veterinario(id_veterinario: int, datos):
    veterinario = obtener_veterinario(id_veterinario)
    if veterinario is None:
        return None

    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise ValueError("Debe proporcionar al menos un campo para actualizar")

    if "id_especialidad" in campos:
        _validar_especialidad(campos["id_especialidad"])

    veterinario_repository.actualizar_veterinario(id_veterinario, datos)
    return {
        "mensaje": "Veterinario actualizado correctamente",
        "id_veterinario": id_veterinario
    }


def actualizar_estado_veterinario(id_veterinario: int, estado: str):
    veterinario = obtener_veterinario(id_veterinario)
    if veterinario is None:
        return None

    veterinario_repository.actualizar_estado_veterinario(id_veterinario, estado)
    return {
        "mensaje": "Estado del veterinario actualizado correctamente",
        "id_veterinario": id_veterinario,
        "estado": estado
    }
