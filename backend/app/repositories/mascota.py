
from backend.app.database.connection import get_connection


# ==========================================
# 1. LISTAR MASCOTAS ACTIVAS
# ==========================================

def listar_mascotas():

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM mascota
            WHERE estado = 'ACTIVO'
            ORDER BY id_mascota DESC
        """)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


def listar_mascotas_por_cliente(id_cliente: int):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM mascota
            WHERE id_cliente = %s
              AND estado = 'ACTIVO'
            ORDER BY id_mascota DESC
        """, (id_cliente,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==========================================
# 2. CONSULTAR MASCOTA POR ID
# ==========================================

def obtener_mascota(id_mascota):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM mascota
            WHERE id_mascota = %s
            AND estado = 'ACTIVO'
        """, (id_mascota,))

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==========================================
# 3. COMPROBAR SI EXISTE UN CLIENTE
# ==========================================

def existe_cliente(id_cliente):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT c.id_cliente
            FROM cliente c
            INNER JOIN usuario u
                ON c.id_usuario = u.id_usuario
            WHERE c.id_cliente = %s
              AND u.estado = 'ACTIVO'
        """, (id_cliente,))

        return cursor.fetchone() is not None

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==========================================
# 4. REGISTRAR MASCOTA
# ==========================================

def registrar_mascota(datos):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO mascota (
                id_cliente,
                nombre,
                especie,
                raza,
                sexo,
                fecha_nacimiento,
                peso_referencial
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.id_cliente,
            datos.nombre,
            datos.especie,
            datos.raza,
            datos.sexo,
            datos.fecha_nacimiento,
            datos.peso_referencial
        ))

        id_mascota = cursor.lastrowid

        conexion.commit()

        return id_mascota

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==========================================
# 5. ACTUALIZAR MASCOTA
# ==========================================

def actualizar_mascota(id_mascota, datos):

    conexion = None
    cursor = None

    try:
        # Obtener solamente los campos enviados
        campos = datos.model_dump(exclude_unset=True)

        # Si no enviaron ningún campo, no hay nada que actualizar
        if not campos:
            return False

        # Construir dinámicamente la consulta SQL
        columnas_permitidas = {
            "id_cliente",
            "nombre",
            "especie",
            "raza",
            "sexo",
            "fecha_nacimiento",
            "peso_referencial"
        }

        # Verificar que los campos sean permitidos
        if not set(campos).issubset(columnas_permitidas):
            raise ValueError("Se enviaron campos no permitidos")

        asignaciones = ", ".join(
            f"{campo} = %s" for campo in campos
        )

        valores = list(campos.values())
        valores.append(id_mascota)

        conexion = get_connection()
        cursor = conexion.cursor()

        # Verificar que la mascota exista y esté activa
        cursor.execute("""
            SELECT id_mascota
            FROM mascota
            WHERE id_mascota = %s
            AND estado = 'ACTIVO'
        """, (id_mascota,))

        mascota = cursor.fetchone()

        if mascota is None:
            return None

        # Ejecutar la actualización
        cursor.execute(f"""
            UPDATE mascota
            SET {asignaciones}
            WHERE id_mascota = %s
            AND estado = 'ACTIVO'
        """, tuple(valores))

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

# ==========================================
# 6. DESACTIVAR MASCOTA
# ==========================================

def desactivar_mascota(id_mascota):

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE mascota
            SET estado = 'INACTIVO'
            WHERE id_mascota = %s
            AND estado = 'ACTIVO'
        """, (id_mascota,))

        filas_afectadas = cursor.rowcount

        conexion.commit()

        return filas_afectadas > 0

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()
