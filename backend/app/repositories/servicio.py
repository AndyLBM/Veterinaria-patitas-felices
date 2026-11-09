from backend.app.database.connection import get_connection


def registrar_servicio(datos):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO servicio (
                nombre,
                descripcion,
                duracion_minutos,
                precio
            )
            VALUES (%s, %s, %s, %s)
        """, (
            datos.nombre,
            datos.descripcion,
            datos.duracion_minutos,
            datos.precio
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


def listar_servicios():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_servicio,
                nombre,
                descripcion,
                duracion_minutos,
                precio,
                estado
            FROM servicio
            ORDER BY nombre
        """)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_servicio(id_servicio: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_servicio,
                nombre,
                descripcion,
                duracion_minutos,
                precio,
                estado
            FROM servicio
            WHERE id_servicio = %s
        """, (id_servicio,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_servicio(id_servicio: int, datos):
    campos = datos.model_dump(exclude_unset=True)

    if not campos:
        return False

    columnas_permitidas = {
        "nombre",
        "descripcion",
        "duracion_minutos",
        "precio"
    }
    if not set(campos).issubset(columnas_permitidas):
        raise ValueError("Se enviaron campos no permitidos")

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        asignaciones = ", ".join(f"{campo} = %s" for campo in campos)
        valores = [*campos.values(), id_servicio]

        cursor.execute(
            f"UPDATE servicio SET {asignaciones} WHERE id_servicio = %s",
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


def actualizar_estado_servicio(id_servicio: int, estado: str):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE servicio
            SET estado = %s
            WHERE id_servicio = %s
        """, (estado, id_servicio))

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
