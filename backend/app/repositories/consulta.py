from backend.app.database.connection import get_connection


def _contexto_bloqueado(cursor,id_atencion,id_veterinario):
    cursor.execute("SELECT a.id_atencion,c.id_veterinario,c.estado FROM atencion a INNER JOIN cita c ON c.id_cita=a.id_cita WHERE a.id_atencion=%s FOR UPDATE",(id_atencion,))
    fila=cursor.fetchone()
    if fila is None: raise LookupError("Atención no encontrada")
    if fila["id_veterinario"] != id_veterinario: raise PermissionError("No tienes permisos sobre esta atención")
    if fila["estado"] != "EN_ATENCION": raise ValueError("La cita debe estar EN_ATENCION")


def obtener_consulta(id_atencion):
    conexion=cursor=None
    try:
        conexion=get_connection(); cursor=conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_consulta,id_atencion,diagnostico,tratamiento,observaciones FROM consulta WHERE id_atencion=%s",(id_atencion,))
        return cursor.fetchone()
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def registrar_consulta(id_atencion,id_veterinario,datos):
    conexion=cursor=None
    try:
        conexion=get_connection(); conexion.start_transaction(); cursor=conexion.cursor(dictionary=True)
        _contexto_bloqueado(cursor,id_atencion,id_veterinario)
        cursor.execute("SELECT id_consulta FROM consulta WHERE id_atencion=%s FOR UPDATE",(id_atencion,))
        if cursor.fetchone(): raise ValueError("La atención ya tiene una consulta")
        cursor.execute("INSERT INTO consulta (id_atencion,diagnostico,tratamiento,observaciones) VALUES (%s,%s,%s,%s)",(id_atencion,datos.diagnostico,datos.tratamiento,datos.observaciones))
        resultado=cursor.lastrowid; conexion.commit(); return resultado
    except Exception:
        if conexion and conexion.is_connected(): conexion.rollback()
        raise
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def actualizar_consulta(id_atencion,id_veterinario,datos):
    campos=datos.model_dump(exclude_unset=True)
    if not campos: raise ValueError("Debe proporcionar al menos un campo para actualizar")
    conexion=cursor=None
    try:
        conexion=get_connection(); conexion.start_transaction(); cursor=conexion.cursor(dictionary=True)
        _contexto_bloqueado(cursor,id_atencion,id_veterinario)
        cursor.execute("SELECT id_consulta FROM consulta WHERE id_atencion=%s FOR UPDATE",(id_atencion,))
        if cursor.fetchone() is None: raise LookupError("Consulta no encontrada")
        asignaciones=", ".join(f"{campo} = %s" for campo in campos)
        cursor.execute(f"UPDATE consulta SET {asignaciones} WHERE id_atencion=%s",tuple([*campos.values(),id_atencion]))
        conexion.commit(); return True
    except Exception:
        if conexion and conexion.is_connected(): conexion.rollback()
        raise
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()
