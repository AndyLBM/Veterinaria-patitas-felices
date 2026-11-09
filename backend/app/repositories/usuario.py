from backend.app.database.connection import get_connection


def listar_usuarios():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.id_rol,
                r.nombre AS rol,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_registro,
                c.id_cliente,
                v.id_veterinario
            FROM usuario u
            INNER JOIN rol r
                ON r.id_rol = u.id_rol
            LEFT JOIN cliente c
                ON c.id_usuario = u.id_usuario
            LEFT JOIN veterinario v
                ON v.id_usuario = u.id_usuario
            ORDER BY u.id_usuario DESC
        """)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_usuario_administracion(id_usuario: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id_usuario,
                u.id_rol,
                r.nombre AS rol,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_registro,
                c.id_cliente,
                v.id_veterinario
            FROM usuario u
            INNER JOIN rol r
                ON r.id_rol = u.id_rol
            LEFT JOIN cliente c
                ON c.id_usuario = u.id_usuario
            LEFT JOIN veterinario v
                ON v.id_usuario = u.id_usuario
            WHERE u.id_usuario = %s
        """, (id_usuario,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_estado_usuario(id_usuario: int, estado: str):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuario
            SET estado = %s
            WHERE id_usuario = %s
        """, (estado, id_usuario))

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
