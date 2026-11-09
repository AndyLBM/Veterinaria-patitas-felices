
from backend.app.database.connection import get_connection


def registrar_cliente(datos, password_hash):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        # 1. Registrar los datos del usuario
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
            3,
            datos.nombre,
            datos.apellido,
            datos.correo,
            password_hash,
            datos.telefono
        ))

        # 2. Obtener el ID generado por MySQL
        id_usuario = cursor.lastrowid

        # 3. Crear el registro relacionado en cliente
        cursor.execute("""
            INSERT INTO cliente (id_usuario)
            VALUES (%s)
        """, (id_usuario,))

        # 4. Obtener el ID del cliente
        id_cliente = cursor.lastrowid

        # 5. Confirmar ambas operaciones
        conexion.commit()

        return {
            "id_cliente": id_cliente,
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

def listar_clientes():

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id_cliente,
                u.id_usuario,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_registro
            FROM cliente c
            INNER JOIN usuario u
                ON c.id_usuario = u.id_usuario
            WHERE u.estado = 'ACTIVO'
            ORDER BY c.id_cliente DESC
        """)

        clientes = cursor.fetchall()

        return clientes

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


def obtener_cliente(id_cliente):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id_cliente,
                u.id_usuario,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.estado,
                u.fecha_registro
            FROM cliente c
            INNER JOIN usuario u
                ON c.id_usuario = u.id_usuario
            WHERE c.id_cliente = %s
              AND u.estado = 'ACTIVO'
        """, (id_cliente,))

        cliente = cursor.fetchone()

        return cliente

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


def obtener_cliente_por_usuario(id_usuario: int):
    """Obtiene la cuenta de cliente activa asociada a un usuario."""
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id_cliente,
                c.id_usuario
            FROM cliente c
            INNER JOIN usuario u
                ON c.id_usuario = u.id_usuario
            WHERE c.id_usuario = %s
              AND u.estado = 'ACTIVO'
            LIMIT 1
        """, (id_usuario,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

def actualizar_cliente(id_cliente, datos):

    conexion = None
    cursor = None

    try:
        campos = datos.model_dump(exclude_unset=True)

        if not campos:
            return False

        columnas_permitidas = {
            "nombre",
            "apellido",
            "correo",
            "telefono"
        }

        if not set(campos).issubset(columnas_permitidas):
            raise ValueError("Se enviaron campos no permitidos")

        conexion = get_connection()
        cursor = conexion.cursor()

        # 1. Buscar el usuario relacionado con el cliente
        cursor.execute("""
            SELECT u.id_usuario
            FROM cliente c
            INNER JOIN usuario u
                ON c.id_usuario = u.id_usuario
            WHERE c.id_cliente = %s
              AND u.estado = 'ACTIVO'
        """, (id_cliente,))

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        id_usuario = resultado[0]

        # 2. Construir la actualización con campos permitidos
        asignaciones = ", ".join(
            f"{campo} = %s" for campo in campos
        )

        valores = list(campos.values())
        valores.append(id_usuario)

        # 3. Actualizar los datos del usuario
        cursor.execute(
            f"UPDATE usuario SET {asignaciones} WHERE id_usuario = %s",
            tuple(valores)
        )

        # 4. Confirmar los cambios
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

def desactivar_cliente(id_cliente):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        # 1. Buscar el usuario relacionado con el cliente
        cursor.execute("""
            SELECT u.id_usuario
            FROM cliente c
            INNER JOIN usuario u
                ON c.id_usuario = u.id_usuario
            WHERE c.id_cliente = %s
              AND u.estado = 'ACTIVO'
        """, (id_cliente,))

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        id_usuario = resultado[0]

        # 2. Cambiar el estado del usuario
        cursor.execute("""
            UPDATE usuario
            SET estado = 'INACTIVO'
            WHERE id_usuario = %s
        """, (id_usuario,))

        # 3. Confirmar la operación
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
