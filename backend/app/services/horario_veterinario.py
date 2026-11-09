from datetime import time, timedelta

from backend.app.repositories import horario_veterinario as horario_repository
from backend.app.repositories import veterinario as veterinario_repository
from backend.app.schemas.horario_veterinario import segundos_desde_medianoche


def _obtener_veterinario_activo(id_veterinario: int):
    veterinario = veterinario_repository.obtener_veterinario(id_veterinario)
    if veterinario is None:
        raise ValueError("El veterinario indicado no existe")

    if veterinario["estado"] != "ACTIVO":
        raise ValueError("No se puede asignar horario a un veterinario inactivo")

    return veterinario


def _validar_rango(hora_inicio, hora_fin):
    if segundos_desde_medianoche(hora_inicio) >= segundos_desde_medianoche(hora_fin):
        raise ValueError("La hora de inicio debe ser anterior a la hora de fin")


def _serializar_horario(horario):
    if horario is None:
        return None
    resultado = dict(horario)
    for campo in ("hora_inicio", "hora_fin"):
        valor = resultado[campo]
        if isinstance(valor, timedelta):
            segundos = int(valor.total_seconds())
            resultado[campo] = f"{segundos // 3600:02d}:{segundos % 3600 // 60:02d}:{segundos % 60:02d}"
        elif isinstance(valor, time):
            resultado[campo] = valor.isoformat(timespec="seconds")
    return resultado


def listar_horarios(id_veterinario: int | None = None):
    return [_serializar_horario(h) for h in horario_repository.listar_horarios(id_veterinario)]


def obtener_horario(id_horario: int):
    return _serializar_horario(horario_repository.obtener_horario(id_horario))


def registrar_horario(datos):
    _obtener_veterinario_activo(datos.id_veterinario)

    if horario_repository.existe_solapamiento(
        datos.id_veterinario,
        datos.dia_semana,
        datos.hora_inicio,
        datos.hora_fin
    ):
        raise ValueError("El horario se solapa con otro registro del veterinario")

    id_horario = horario_repository.registrar_horario(datos)
    return {
        "mensaje": "Horario registrado correctamente",
        "id_horario": id_horario
    }


def actualizar_horario(id_horario: int, datos):
    # Las validaciones internas siguen trabajando con TIME/timedelta de MySQL.
    horario = horario_repository.obtener_horario(id_horario)
    if horario is None:
        return None

    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise ValueError("Debe proporcionar al menos un campo para actualizar")

    _obtener_veterinario_activo(horario["id_veterinario"])

    dia_semana = campos.get("dia_semana", horario["dia_semana"])
    hora_inicio = campos.get("hora_inicio", horario["hora_inicio"])
    hora_fin = campos.get("hora_fin", horario["hora_fin"])
    _validar_rango(hora_inicio, hora_fin)

    if horario_repository.existe_solapamiento(
        horario["id_veterinario"],
        dia_semana,
        hora_inicio,
        hora_fin,
        id_horario
    ):
        raise ValueError("El horario se solapa con otro registro del veterinario")

    horario_repository.actualizar_horario(id_horario, datos)
    return {
        "mensaje": "Horario actualizado correctamente",
        "id_horario": id_horario
    }
