from backend.app.database.connection import get_connection


def obtener_usuario_por_correo(correo: str):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_usuario,
                id_rol,
                nombre,
                apellido,
                correo,
                password_hash,
                estado
            FROM usuario
            WHERE correo = %s
            LIMIT 1
        """, (correo,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_usuario_por_id(id_usuario: int):
    """Obtiene el estado y rol vigentes de un usuario autenticado."""
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_usuario,
                id_rol,
                estado
            FROM usuario
            WHERE id_usuario = %s
            LIMIT 1
        """, (id_usuario,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
