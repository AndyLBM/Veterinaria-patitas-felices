from backend.app.database.connection import get_connection


def registrar_especialidad(datos):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO especialidad (nombre, descripcion)
            VALUES (%s, %s)
        """, (datos.nombre, datos.descripcion))

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


def listar_especialidades():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_especialidad, nombre, descripcion
            FROM especialidad
            ORDER BY nombre
        """)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_especialidad(id_especialidad: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_especialidad, nombre, descripcion
            FROM especialidad
            WHERE id_especialidad = %s
        """, (id_especialidad,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_especialidad(id_especialidad: int, datos):
    campos = datos.model_dump(exclude_unset=True)

    if not campos:
        return False

    columnas_permitidas = {"nombre", "descripcion"}
    if not set(campos).issubset(columnas_permitidas):
        raise ValueError("Se enviaron campos no permitidos")

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        asignaciones = ", ".join(f"{campo} = %s" for campo in campos)
        valores = [*campos.values(), id_especialidad]

        cursor.execute(
            f"UPDATE especialidad SET {asignaciones} WHERE id_especialidad = %s",
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
