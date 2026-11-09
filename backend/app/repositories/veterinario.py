from backend.app.database.connection import get_connection


def registrar_veterinario(datos, password_hash: str):
    """Crea en una sola transacción la cuenta y el perfil veterinario."""
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO usuario (
                id_rol,
                nombre,
                apellido,
                correo,
                password_hash,
                telefono
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            2,
            datos.nombre,
            datos.apellido,
            datos.correo,
            password_hash,
            datos.telefono
        ))
        id_usuario = cursor.lastrowid

        cursor.execute("""
            INSERT INTO veterinario (
                id_usuario,
                id_especialidad,
                numero_colegiatura
            )
            VALUES (%s, %s, %s)
        """, (
            id_usuario,
            datos.id_especialidad,
            datos.numero_colegiatura
        ))
        id_veterinario = cursor.lastrowid

        conexion.commit()
        return {
            "id_veterinario": id_veterinario,
            "id_usuario": id_usuario
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


def listar_veterinarios():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                v.id_veterinario,
                v.id_usuario,
                v.id_especialidad,
                v.numero_colegiatura,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_registro,
                e.nombre AS especialidad
            FROM veterinario v
            INNER JOIN usuario u
                ON u.id_usuario = v.id_usuario
            INNER JOIN especialidad e
                ON e.id_especialidad = v.id_especialidad
            ORDER BY v.id_veterinario DESC
        """)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_veterinario(id_veterinario: int):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                v.id_veterinario,
                v.id_usuario,
                v.id_especialidad,
                v.numero_colegiatura,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_registro,
                e.nombre AS especialidad
            FROM veterinario v
            INNER JOIN usuario u
                ON u.id_usuario = v.id_usuario
            INNER JOIN especialidad e
                ON e.id_especialidad = v.id_especialidad
            WHERE v.id_veterinario = %s
        """, (id_veterinario,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_veterinario_por_usuario(id_usuario: int):
    conexion = cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.id_veterinario, v.id_usuario, u.estado
            FROM veterinario v
            INNER JOIN usuario u ON u.id_usuario = v.id_usuario
            WHERE v.id_usuario = %s
        """, (id_usuario,))
        return cursor.fetchone()
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def actualizar_veterinario(id_veterinario: int, datos):
    campos = datos.model_dump(exclude_unset=True)

    if not campos:
        return False

    campos_usuario_permitidos = {"nombre", "apellido", "correo", "telefono"}
    campos_veterinario_permitidos = {"id_especialidad", "numero_colegiatura"}
    columnas_permitidas = campos_usuario_permitidos | campos_veterinario_permitidos

    if not set(campos).issubset(columnas_permitidas):
        raise ValueError("Se enviaron campos no permitidos")

    campos_usuario = {
        campo: valor
        for campo, valor in campos.items()
        if campo in campos_usuario_permitidos
    }
    campos_veterinario = {
        campo: valor
        for campo, valor in campos.items()
        if campo in campos_veterinario_permitidos
    }

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        if campos_usuario:
            asignaciones = ", ".join(
                f"{campo} = %s" for campo in campos_usuario
            )
            valores = [*campos_usuario.values(), id_veterinario]
            cursor.execute(f"""
                UPDATE usuario u
                INNER JOIN veterinario v
                    ON v.id_usuario = u.id_usuario
                SET {asignaciones}
                WHERE v.id_veterinario = %s
            """, tuple(valores))

        if campos_veterinario:
            asignaciones = ", ".join(
                f"{campo} = %s" for campo in campos_veterinario
            )
            valores = [*campos_veterinario.values(), id_veterinario]
            cursor.execute(
                f"UPDATE veterinario SET {asignaciones} "
                "WHERE id_veterinario = %s",
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


def actualizar_estado_veterinario(id_veterinario: int, estado: str):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuario u
            INNER JOIN veterinario v
                ON v.id_usuario = u.id_usuario
            SET u.estado = %s
            WHERE v.id_veterinario = %s
        """, (estado, id_veterinario))

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
