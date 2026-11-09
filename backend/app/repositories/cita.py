from datetime import datetime, time, timedelta

from backend.app.database.connection import get_connection
from backend.app.core.fechas import validar_inicio_no_pasado


ESTADOS_BLOQUEANTES = ("PROGRAMADA", "CONFIRMADA", "EN_ATENCION")


CONSULTA_CITA_DETALLE = """
    SELECT
        c.id_cita,
        c.id_mascota,
        c.id_veterinario,
        c.id_servicio,
        c.fecha_inicio,
        c.fecha_fin,
        c.duracion_minutos,
        c.motivo,
        c.estado,
        c.fecha_registro,
        m.id_cliente,
        uc.nombre AS nombre_cliente,
        uc.apellido AS apellido_cliente,
        uc.telefono AS telefono_cliente,
        m.nombre AS nombre_mascota,
        m.especie AS especie_mascota,
        m.estado AS estado_mascota,
        uc.estado AS estado_cliente,
        v.numero_colegiatura,
        uv.nombre AS nombre_veterinario,
        uv.apellido AS apellido_veterinario,
        uv.estado AS estado_veterinario,
        s.nombre AS nombre_servicio,
        s.estado AS estado_servicio
    FROM cita c
    INNER JOIN mascota m
        ON m.id_mascota = c.id_mascota
    INNER JOIN cliente cl
        ON cl.id_cliente = m.id_cliente
    INNER JOIN usuario uc
        ON uc.id_usuario = cl.id_usuario
    INNER JOIN veterinario v
        ON v.id_veterinario = c.id_veterinario
    INNER JOIN usuario uv
        ON uv.id_usuario = v.id_usuario
    INNER JOIN servicio s
        ON s.id_servicio = c.id_servicio
"""


def _segundos_desde_medianoche(valor: time | timedelta) -> float:
    if isinstance(valor, timedelta):
        return valor.total_seconds()

    return (
        valor.hour * 3600
        + valor.minute * 60
        + valor.second
        + valor.microsecond / 1_000_000
    )


def _iniciar_transaccion(conexion):
    conexion.start_transaction()


def obtener_cita(id_cita: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            CONSULTA_CITA_DETALLE + " WHERE c.id_cita = %s",
            (id_cita,)
        )
        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def listar_citas_administracion(
    fecha_desde=None,
    fecha_hasta=None,
    estado: str | None = None,
    id_veterinario: int | None = None,
    id_cliente: int | None = None
):
    condiciones = []
    parametros = []

    if fecha_desde is not None:
        condiciones.append("c.fecha_inicio >= %s")
        parametros.append(datetime.combine(fecha_desde, time.min))

    if fecha_hasta is not None:
        condiciones.append("c.fecha_inicio < %s")
        parametros.append(datetime.combine(fecha_hasta + timedelta(days=1), time.min))

    if estado is not None:
        condiciones.append("c.estado = %s")
        parametros.append(estado)

    if id_veterinario is not None:
        condiciones.append("c.id_veterinario = %s")
        parametros.append(id_veterinario)

    if id_cliente is not None:
        condiciones.append("m.id_cliente = %s")
        parametros.append(id_cliente)

    consulta = CONSULTA_CITA_DETALLE
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    consulta += " ORDER BY c.fecha_inicio DESC, c.id_cita DESC"

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(consulta, tuple(parametros))
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def listar_citas_por_cliente(id_cliente: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            CONSULTA_CITA_DETALLE
            + " WHERE m.id_cliente = %s ORDER BY c.fecha_inicio DESC, c.id_cita DESC",
            (id_cliente,)
        )
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def listar_citas_bloqueantes(
    id_veterinario: int, fecha, id_cita_excluida: int | None = None,
    id_mascota: int | None = None
):
    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = inicio_dia + timedelta(days=1)
    marcadores = ", ".join(["%s"] * len(ESTADOS_BLOQUEANTES))

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        filtro_recurso = "id_veterinario = %s"
        parametros_recurso = [id_veterinario]
        if id_mascota is not None:
            filtro_recurso = "(id_veterinario = %s OR id_mascota = %s)"
            parametros_recurso.append(id_mascota)
        filtro_exclusion = " AND id_cita <> %s" if id_cita_excluida is not None else ""
        parametros = [*parametros_recurso, *ESTADOS_BLOQUEANTES, fin_dia, inicio_dia]
        if id_cita_excluida is not None:
            parametros.append(id_cita_excluida)
        cursor.execute(f"""
            SELECT id_cita, fecha_inicio, fecha_fin, estado
            FROM cita
            WHERE {filtro_recurso}
              AND estado IN ({marcadores})
              AND fecha_inicio < %s
              AND fecha_fin > %s
              {filtro_exclusion}
            ORDER BY fecha_inicio
        """, tuple(parametros))
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def _obtener_mascota_bloqueada(cursor, id_mascota: int):
    cursor.execute("""
        SELECT
            m.id_mascota,
            m.id_cliente,
            m.estado AS estado_mascota,
            u.estado AS estado_cliente
        FROM mascota m
        INNER JOIN cliente c
            ON c.id_cliente = m.id_cliente
        INNER JOIN usuario u
            ON u.id_usuario = c.id_usuario
        WHERE m.id_mascota = %s
        FOR UPDATE
    """, (id_mascota,))
    return cursor.fetchone()


def _obtener_veterinario_bloqueado(cursor, id_veterinario: int):
    cursor.execute("""
        SELECT v.id_veterinario, u.estado
        FROM veterinario v
        INNER JOIN usuario u
            ON u.id_usuario = v.id_usuario
        WHERE v.id_veterinario = %s
        FOR UPDATE
    """, (id_veterinario,))
    return cursor.fetchone()


def _obtener_servicio_bloqueado(cursor, id_servicio: int):
    cursor.execute("""
        SELECT id_servicio, duracion_minutos, estado
        FROM servicio
        WHERE id_servicio = %s
        FOR UPDATE
    """, (id_servicio,))
    return cursor.fetchone()


def _obtener_horarios_bloqueados(cursor, id_veterinario: int, dia_semana: int):
    cursor.execute("""
        SELECT hora_inicio, hora_fin
        FROM horario_veterinario
        WHERE id_veterinario = %s
          AND dia_semana = %s
        ORDER BY hora_inicio
        FOR UPDATE
    """, (id_veterinario, dia_semana))
    return cursor.fetchall()


def _cita_esta_dentro_de_horario(fecha_inicio, fecha_fin, horarios) -> bool:
    if fecha_inicio.date() != fecha_fin.date():
        return False

    inicio = _segundos_desde_medianoche(fecha_inicio.time())
    fin = _segundos_desde_medianoche(fecha_fin.time())

    return any(
        inicio >= _segundos_desde_medianoche(horario["hora_inicio"])
        and fin <= _segundos_desde_medianoche(horario["hora_fin"])
        for horario in horarios
    )


def _hay_solapamiento_bloqueado(
    cursor,
    columna: str,
    identificador: int,
    fecha_inicio,
    fecha_fin,
    id_cita_excluida: int | None = None
) -> bool:
    if columna not in {"id_veterinario", "id_mascota"}:
        raise ValueError("Columna de validación no permitida")

    marcadores = ", ".join(["%s"] * len(ESTADOS_BLOQUEANTES))
    consulta = f"""
        SELECT id_cita
        FROM cita
        WHERE {columna} = %s
          AND estado IN ({marcadores})
          AND fecha_inicio < %s
          AND fecha_fin > %s
    """
    parametros = [identificador, *ESTADOS_BLOQUEANTES, fecha_fin, fecha_inicio]

    if id_cita_excluida is not None:
        consulta += " AND id_cita <> %s"
        parametros.append(id_cita_excluida)

    consulta += " FOR UPDATE"
    cursor.execute(consulta, tuple(parametros))
    return cursor.fetchone() is not None


def _validar_contexto_mascota(mascota, id_cliente_permitido: int | None):
    if mascota is None:
        raise LookupError("Mascota no encontrada")

    if mascota["estado_mascota"] != "ACTIVO":
        raise ValueError("La mascota no está activa")

    if mascota["estado_cliente"] != "ACTIVO":
        raise ValueError("La cuenta del cliente no está activa")

    if (
        id_cliente_permitido is not None
        and mascota["id_cliente"] != id_cliente_permitido
    ):
        raise PermissionError("No tienes permisos sobre la mascota indicada")


def _validar_veterinario_activo(veterinario):
    if veterinario is None:
        raise LookupError("Veterinario no encontrado")

    if veterinario["estado"] != "ACTIVO":
        raise ValueError("El veterinario no está activo")


def registrar_cita_segura(
    id_mascota: int,
    id_veterinario: int,
    id_servicio: int,
    fecha_inicio,
    motivo: str | None,
    id_cliente_permitido: int | None = None
):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        _iniciar_transaccion(conexion)
        cursor = conexion.cursor(dictionary=True)

        mascota = _obtener_mascota_bloqueada(cursor, id_mascota)
        _validar_contexto_mascota(mascota, id_cliente_permitido)

        veterinario = _obtener_veterinario_bloqueado(cursor, id_veterinario)
        _validar_veterinario_activo(veterinario)

        servicio = _obtener_servicio_bloqueado(cursor, id_servicio)
        if servicio is None:
            raise LookupError("Servicio no encontrado")
        if servicio["estado"] != "ACTIVO":
            raise ValueError("El servicio no está activo")

        duracion_minutos = servicio["duracion_minutos"]
        fecha_fin = fecha_inicio + timedelta(minutes=duracion_minutos)
        horarios = _obtener_horarios_bloqueados(
            cursor,
            id_veterinario,
            fecha_inicio.isoweekday()
        )

        if not _cita_esta_dentro_de_horario(fecha_inicio, fecha_fin, horarios):
            raise ValueError("La cita no está dentro del horario del veterinario")

        if _hay_solapamiento_bloqueado(
            cursor,
            "id_veterinario",
            id_veterinario,
            fecha_inicio,
            fecha_fin
        ):
            raise ValueError("El veterinario ya tiene una cita en ese horario")

        if _hay_solapamiento_bloqueado(
            cursor,
            "id_mascota",
            id_mascota,
            fecha_inicio,
            fecha_fin
        ):
            raise ValueError("La mascota ya tiene una cita en ese horario")

        # Los bloqueos/esperas ya terminaron: validar contra el reloj vigente.
        validar_inicio_no_pasado(fecha_inicio)
        cursor.execute("""
            INSERT INTO cita (
                id_mascota,
                id_veterinario,
                id_servicio,
                fecha_inicio,
                fecha_fin,
                duracion_minutos,
                motivo,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'PROGRAMADA')
        """, (
            id_mascota,
            id_veterinario,
            id_servicio,
            fecha_inicio,
            fecha_fin,
            duracion_minutos,
            motivo
        ))

        id_cita = cursor.lastrowid
        conexion.commit()
        return {
            "id_cita": id_cita,
            "fecha_fin": fecha_fin,
            "duracion_minutos": duracion_minutos,
            "estado": "PROGRAMADA"
        }

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def _obtener_cita_bloqueada(cursor, id_cita: int):
    cursor.execute("""
        SELECT
            c.id_cita,
            c.id_mascota,
            c.id_veterinario,
            c.id_servicio,
            c.fecha_inicio,
            c.fecha_fin,
            c.duracion_minutos,
            c.estado,
            m.id_cliente,
            m.estado AS estado_mascota,
            uc.estado AS estado_cliente
        FROM cita c
        INNER JOIN mascota m
            ON m.id_mascota = c.id_mascota
        INNER JOIN cliente cl
            ON cl.id_cliente = m.id_cliente
        INNER JOIN usuario uc
            ON uc.id_usuario = cl.id_usuario
        WHERE c.id_cita = %s
        FOR UPDATE
    """, (id_cita,))
    return cursor.fetchone()


def reprogramar_cita_segura(
    id_cita: int,
    id_veterinario: int,
    fecha_inicio,
    id_cliente_permitido: int | None = None,
    plazo_minimo=None
):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        _iniciar_transaccion(conexion)
        cursor = conexion.cursor(dictionary=True)

        cita = _obtener_cita_bloqueada(cursor, id_cita)
        if cita is None:
            raise LookupError("Cita no encontrada")

        _validar_contexto_mascota(cita, id_cliente_permitido)

        if cita["estado"] not in {"PROGRAMADA", "CONFIRMADA"}:
            raise ValueError("La cita no se puede reprogramar en su estado actual")

        if plazo_minimo is not None and cita["fecha_inicio"] < plazo_minimo:
            raise ValueError(
                "La cita solo puede reprogramarse hasta 24 horas antes de su inicio"
            )

        veterinario = _obtener_veterinario_bloqueado(cursor, id_veterinario)
        _validar_veterinario_activo(veterinario)

        fecha_fin = fecha_inicio + timedelta(minutes=cita["duracion_minutos"])
        horarios = _obtener_horarios_bloqueados(
            cursor,
            id_veterinario,
            fecha_inicio.isoweekday()
        )

        if not _cita_esta_dentro_de_horario(fecha_inicio, fecha_fin, horarios):
            raise ValueError("La cita no está dentro del horario del veterinario")

        if _hay_solapamiento_bloqueado(
            cursor,
            "id_veterinario",
            id_veterinario,
            fecha_inicio,
            fecha_fin,
            id_cita
        ):
            raise ValueError("El veterinario ya tiene una cita en ese horario")

        if _hay_solapamiento_bloqueado(
            cursor,
            "id_mascota",
            cita["id_mascota"],
            fecha_inicio,
            fecha_fin,
            id_cita
        ):
            raise ValueError("La mascota ya tiene una cita en ese horario")

        validar_inicio_no_pasado(fecha_inicio)
        cursor.execute("""
            UPDATE cita
            SET id_veterinario = %s,
                fecha_inicio = %s,
                fecha_fin = %s
            WHERE id_cita = %s
        """, (id_veterinario, fecha_inicio, fecha_fin, id_cita))

        conexion.commit()
        return {"fecha_fin": fecha_fin}

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def cancelar_cita_segura(
    id_cita: int,
    id_cliente_permitido: int | None = None,
    plazo_minimo=None
):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        _iniciar_transaccion(conexion)
        cursor = conexion.cursor(dictionary=True)

        cita = _obtener_cita_bloqueada(cursor, id_cita)
        if cita is None:
            raise LookupError("Cita no encontrada")

        _validar_contexto_mascota(cita, id_cliente_permitido)

        if cita["estado"] not in {"PROGRAMADA", "CONFIRMADA"}:
            raise ValueError("La cita no se puede cancelar en su estado actual")

        if plazo_minimo is not None and cita["fecha_inicio"] < plazo_minimo:
            raise ValueError(
                "La cita solo puede cancelarse hasta 24 horas antes de su inicio"
            )

        cursor.execute("""
            UPDATE cita
            SET estado = 'CANCELADA'
            WHERE id_cita = %s
        """, (id_cita,))
        conexion.commit()
        return True

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_estado_cita_seguro(
    id_cita: int,
    estado_nuevo: str,
    estados_origen_permitidos: set[str]
):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        _iniciar_transaccion(conexion)
        cursor = conexion.cursor(dictionary=True)

        cita = _obtener_cita_bloqueada(cursor, id_cita)
        if cita is None:
            raise LookupError("Cita no encontrada")

        if cita["estado"] not in estados_origen_permitidos:
            raise ValueError("El estado de la cita cambió; vuelva a intentarlo")

        cursor.execute("""
            UPDATE cita
            SET estado = %s
            WHERE id_cita = %s
        """, (estado_nuevo, id_cita))
        conexion.commit()
        return True

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
