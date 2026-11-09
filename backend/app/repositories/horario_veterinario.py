from backend.app.database.connection import get_connection


def listar_horarios(id_veterinario: int | None = None):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                h.id_horario,
                h.id_veterinario,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin,
                u.nombre AS nombre_veterinario,
                u.apellido AS apellido_veterinario,
                u.estado AS estado_veterinario
            FROM horario_veterinario h
            INNER JOIN veterinario v
                ON v.id_veterinario = h.id_veterinario
            INNER JOIN usuario u
                ON u.id_usuario = v.id_usuario
        """
        parametros = ()

        if id_veterinario is not None:
            consulta += " WHERE h.id_veterinario = %s"
            parametros = (id_veterinario,)

        consulta += " ORDER BY h.id_veterinario, h.dia_semana, h.hora_inicio"
        cursor.execute(consulta, parametros)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_horario(id_horario: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_horario,
                id_veterinario,
                dia_semana,
                hora_inicio,
                hora_fin
            FROM horario_veterinario
            WHERE id_horario = %s
        """, (id_horario,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def existe_solapamiento(
    id_veterinario: int,
    dia_semana: int,
    hora_inicio,
    hora_fin,
    id_horario_excluido: int | None = None
):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        consulta = """
            SELECT id_horario
            FROM horario_veterinario
            WHERE id_veterinario = %s
              AND dia_semana = %s
              AND hora_inicio < %s
              AND hora_fin > %s
        """
        parametros = [id_veterinario, dia_semana, hora_fin, hora_inicio]

        if id_horario_excluido is not None:
            consulta += " AND id_horario <> %s"
            parametros.append(id_horario_excluido)

        consulta += " LIMIT 1"
        cursor.execute(consulta, tuple(parametros))
        return cursor.fetchone() is not None

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def registrar_horario(datos):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO horario_veterinario (
                id_veterinario,
                dia_semana,
                hora_inicio,
                hora_fin
            )
            VALUES (%s, %s, %s, %s)
        """, (
            datos.id_veterinario,
            datos.dia_semana,
            datos.hora_inicio,
            datos.hora_fin
        ))

        conexion.commit()
        return cursor.lastrowid

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_horario(id_horario: int, datos):
    campos = datos.model_dump(exclude_unset=True)

    if not campos:
        return False

    columnas_permitidas = {"dia_semana", "hora_inicio", "hora_fin"}
    if not set(campos).issubset(columnas_permitidas):
        raise ValueError("Se enviaron campos no permitidos")

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        asignaciones = ", ".join(f"{campo} = %s" for campo in campos)
        valores = [*campos.values(), id_horario]
        cursor.execute(
            f"UPDATE horario_veterinario SET {asignaciones} "
            "WHERE id_horario = %s",
            tuple(valores)
        )

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
