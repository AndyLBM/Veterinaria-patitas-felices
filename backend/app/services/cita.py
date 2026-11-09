from datetime import datetime, time, timedelta

from backend.app.core.fechas import ahora_lima
from backend.app.repositories import cita as cita_repository
from backend.app.repositories import atencion as atencion_repository
from backend.app.repositories import horario_veterinario as horario_repository
from backend.app.repositories import servicio as servicio_repository
from backend.app.repositories import veterinario as veterinario_repository


TRANSICIONES_PERMITIDAS = {
    "PROGRAMADA": {"CONFIRMADA", "CANCELADA"},
    "CONFIRMADA": {"EN_ATENCION", "CANCELADA", "NO_ASISTIO"},
    "EN_ATENCION": {"ATENDIDA"},
    "ATENDIDA": set(),
    "CANCELADA": set(),
    "NO_ASISTIO": set(),
}


def _combinar_fecha_hora(fecha, hora) -> datetime:
    if isinstance(hora, timedelta):
        return datetime.combine(fecha, time.min) + hora

    return datetime.combine(fecha, hora)


def _validar_veterinario_activo(id_veterinario: int):
    veterinario = veterinario_repository.obtener_veterinario(id_veterinario)
    if veterinario is None:
        raise ValueError("El veterinario indicado no existe")
    if veterinario["estado"] != "ACTIVO":
        raise ValueError("El veterinario indicado no está activo")

    return veterinario


def _validar_servicio_activo(id_servicio: int):
    servicio = servicio_repository.obtener_servicio(id_servicio)
    if servicio is None:
        raise ValueError("El servicio indicado no existe")
    if servicio["estado"] != "ACTIVO":
        raise ValueError("El servicio indicado no está activo")

    return servicio


def _unir_franjas(franjas):
    resultado = []
    for inicio, fin in sorted(franjas, key=lambda franja: franja[0]):
        if not resultado or inicio > resultado[-1][1]:
            resultado.append([inicio, fin])
            continue

        if fin > resultado[-1][1]:
            resultado[-1][1] = fin

    return [(inicio, fin) for inicio, fin in resultado]


def _calcular_franjas_libres(franjas_horario, citas_bloqueantes, duracion_minutos):
    franjas_libres = []
    duracion = timedelta(minutes=duracion_minutos)

    for inicio_horario, fin_horario in _unir_franjas(franjas_horario):
        cursor = inicio_horario

        for cita in citas_bloqueantes:
            inicio_cita = cita["fecha_inicio"]
            fin_cita = cita["fecha_fin"]

            if fin_cita <= cursor:
                continue
            if inicio_cita >= fin_horario:
                break

            if inicio_cita > cursor:
                fin_libre = min(inicio_cita, fin_horario)
                if fin_libre - cursor >= duracion:
                    franjas_libres.append((cursor, fin_libre))

            if fin_cita > cursor:
                cursor = fin_cita

            if cursor >= fin_horario:
                break

        if fin_horario - cursor >= duracion:
            franjas_libres.append((cursor, fin_horario))

    return franjas_libres


def _disponibilidad(
    veterinario, id_servicio, fecha, duracion_minutos,
    id_cita_excluida=None, id_mascota=None
):
    id_veterinario = veterinario["id_veterinario"]
    horarios = horario_repository.listar_horarios(id_veterinario)
    franjas_horario = [
        (
            _combinar_fecha_hora(fecha, horario["hora_inicio"]),
            _combinar_fecha_hora(fecha, horario["hora_fin"])
        )
        for horario in horarios
        if horario["dia_semana"] == fecha.isoweekday()
    ]
    citas_bloqueantes = cita_repository.listar_citas_bloqueantes(
        id_veterinario,
        fecha,
        id_cita_excluida,
        id_mascota
    )
    franjas_libres = _calcular_franjas_libres(
        franjas_horario,
        citas_bloqueantes,
        duracion_minutos
    )

    return {
        "id_veterinario": veterinario["id_veterinario"],
        "id_servicio": id_servicio,
        "fecha": fecha,
        "dia_semana": fecha.isoweekday(),
        "duracion_minutos": duracion_minutos,
        "zona_horaria": "America/Lima",
        "franjas_disponibles": [
            {"inicio": inicio, "fin": fin}
            for inicio, fin in franjas_libres
        ]
    }


def consultar_disponibilidad(id_veterinario: int, id_servicio: int, fecha):
    veterinario = _validar_veterinario_activo(id_veterinario)
    servicio = _validar_servicio_activo(id_servicio)
    return _disponibilidad(veterinario, id_servicio, fecha, servicio["duracion_minutos"])


def consultar_disponibilidad_reprogramacion(
    id_cita: int, id_veterinario: int, fecha,
    id_cliente_permitido: int | None = None
):
    cita = obtener_cita(id_cita)
    if cita is None:
        raise LookupError("Cita no encontrada")
    if id_cliente_permitido is not None and cita["id_cliente"] != id_cliente_permitido:
        raise PermissionError("No tienes permisos sobre esta cita")
    if cita["estado"] not in {"PROGRAMADA", "CONFIRMADA"}:
        raise ValueError("La cita no se puede reprogramar en su estado actual")
    if id_cliente_permitido is not None and cita["fecha_inicio"] < ahora_lima() + timedelta(hours=24):
        raise ValueError("La cita solo puede reprogramarse hasta 24 horas antes de su inicio")
    veterinario = _validar_veterinario_activo(id_veterinario)
    return {
        "id_cita": id_cita,
        **_disponibilidad(veterinario, cita["id_servicio"], fecha,
                          cita["duracion_minutos"], id_cita, cita["id_mascota"])
    }


def listar_servicios_disponibles():
    return [
        servicio
        for servicio in servicio_repository.listar_servicios()
        if servicio["estado"] == "ACTIVO"
    ]


def listar_veterinarios_disponibles(id_servicio: int, fecha):
    _validar_servicio_activo(id_servicio)
    disponibles = []

    for veterinario in veterinario_repository.listar_veterinarios():
        if veterinario["estado"] != "ACTIVO":
            continue

        disponibilidad = consultar_disponibilidad(
            veterinario["id_veterinario"],
            id_servicio,
            fecha
        )
        if disponibilidad["franjas_disponibles"]:
            disponibles.append({
                "id_veterinario": veterinario["id_veterinario"],
                "nombre": veterinario["nombre"],
                "apellido": veterinario["apellido"],
                "especialidad": veterinario["especialidad"],
                "franjas_disponibles": disponibilidad["franjas_disponibles"]
            })

    return disponibles


def registrar_cita(datos, id_cliente_permitido: int | None = None):
    resultado = cita_repository.registrar_cita_segura(
        id_mascota=datos.id_mascota,
        id_veterinario=datos.id_veterinario,
        id_servicio=datos.id_servicio,
        fecha_inicio=datos.fecha_inicio,
        motivo=datos.motivo,
        id_cliente_permitido=id_cliente_permitido
    )
    return {
        "mensaje": "Cita registrada correctamente",
        **resultado
    }


def listar_citas_administracion(
    fecha_desde=None,
    fecha_hasta=None,
    estado: str | None = None,
    id_veterinario: int | None = None,
    id_cliente: int | None = None
):
    if (
        fecha_desde is not None
        and fecha_hasta is not None
        and fecha_desde > fecha_hasta
    ):
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final")

    return cita_repository.listar_citas_administracion(
        fecha_desde,
        fecha_hasta,
        estado,
        id_veterinario,
        id_cliente
    )


def listar_mis_citas(id_cliente: int):
    return cita_repository.listar_citas_por_cliente(id_cliente)


def listar_mi_agenda(id_veterinario: int, fecha_desde=None, fecha_hasta=None, estado=None):
    return listar_citas_administracion(
        fecha_desde, fecha_hasta, estado, id_veterinario=id_veterinario
    )


def obtener_cita(id_cita: int):
    return cita_repository.obtener_cita(id_cita)


def reprogramar_cita(
    id_cita: int,
    datos,
    id_cliente_permitido: int | None = None
):
    plazo_minimo = None
    if id_cliente_permitido is not None:
        plazo_minimo = ahora_lima() + timedelta(hours=24)

    resultado = cita_repository.reprogramar_cita_segura(
        id_cita=id_cita,
        id_veterinario=datos.id_veterinario,
        fecha_inicio=datos.fecha_inicio,
        id_cliente_permitido=id_cliente_permitido,
        plazo_minimo=plazo_minimo
    )
    return {
        "mensaje": "Cita reprogramada correctamente",
        "id_cita": id_cita,
        **resultado
    }


def cancelar_cita(id_cita: int, id_cliente_permitido: int | None = None):
    plazo_minimo = None
    if id_cliente_permitido is not None:
        plazo_minimo = ahora_lima() + timedelta(hours=24)

    cita_repository.cancelar_cita_segura(
        id_cita,
        id_cliente_permitido,
        plazo_minimo
    )
    return {
        "mensaje": "Cita cancelada correctamente",
        "id_cita": id_cita,
        "estado": "CANCELADA"
    }


def actualizar_estado_cita(id_cita: int, estado_nuevo: str):
    cita = obtener_cita(id_cita)
    if cita is None:
        return None

    estado_actual = cita["estado"]
    if estado_nuevo not in TRANSICIONES_PERMITIDAS[estado_actual]:
        raise ValueError(
            f"No se permite cambiar de {estado_actual} a {estado_nuevo}"
        )

    if estado_nuevo == "ATENDIDA" and not atencion_repository.existe_atencion_completa_por_cita(id_cita):
        raise ValueError("Se requiere atención, triaje y consulta antes de finalizar la cita")

    cita_repository.actualizar_estado_cita_seguro(
        id_cita,
        estado_nuevo,
        {estado_actual}
    )
    return {
        "mensaje": "Estado de la cita actualizado correctamente",
        "id_cita": id_cita,
        "estado": estado_nuevo
    }
