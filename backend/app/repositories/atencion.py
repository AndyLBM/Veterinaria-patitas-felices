from backend.app.database.connection import get_connection


def _obtener_atencion(columna: str, identificador: int):
    if columna not in {"id_atencion", "id_cita"}:
        raise ValueError("Filtro de atención no permitido")
    conexion = cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT a.id_atencion, a.id_cita, a.fecha_atencion, a.observaciones,
                   c.id_veterinario, c.id_mascota, c.estado AS estado_cita
            FROM atencion a
            INNER JOIN cita c ON c.id_cita = a.id_cita
            WHERE a.{columna} = %s
        """, (identificador,))
        return cursor.fetchone()
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def obtener_atencion(id_atencion: int):
    return _obtener_atencion("id_atencion", id_atencion)


def obtener_atencion_por_cita(id_cita: int):
    return _obtener_atencion("id_cita", id_cita)


def registrar_atencion_segura(id_cita: int, id_veterinario: int, observaciones):
    conexion = cursor = None
    try:
        conexion = get_connection()
        conexion.start_transaction()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_cita, id_veterinario, estado
            FROM cita WHERE id_cita = %s FOR UPDATE
        """, (id_cita,))
        cita = cursor.fetchone()
        if cita is None:
            raise LookupError("Cita no encontrada")
        if cita["id_veterinario"] != id_veterinario:
            raise PermissionError("No tienes permisos sobre esta cita")
        if cita["estado"] != "EN_ATENCION":
            raise ValueError("La cita debe estar EN_ATENCION para iniciar una atención")

        cursor.execute("SELECT id_atencion FROM atencion WHERE id_cita = %s FOR UPDATE", (id_cita,))
        if cursor.fetchone() is not None:
            raise ValueError("La cita ya tiene una atención registrada")

        cursor.execute("""
            INSERT INTO atencion (id_cita, observaciones)
            VALUES (%s, %s)
        """, (id_cita, observaciones))
        id_atencion = cursor.lastrowid
        conexion.commit()
        return id_atencion
    except Exception:
        if conexion and conexion.is_connected(): conexion.rollback()
        raise
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def existe_atencion_completa_por_cita(id_cita: int) -> bool:
    conexion = cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT a.id_atencion
            FROM atencion a
            INNER JOIN triaje t ON t.id_atencion = a.id_atencion
            INNER JOIN consulta con ON con.id_atencion = a.id_atencion
            WHERE a.id_cita = %s
        """, (id_cita,))
        return cursor.fetchone() is not None
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()
