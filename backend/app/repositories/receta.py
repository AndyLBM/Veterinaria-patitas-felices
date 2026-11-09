from backend.app.database.connection import get_connection


def obtener_contexto_consulta(id_consulta):
    con = cur = None
    try:
        con = get_connection()
        cur = con.cursor(dictionary=True)
        cur.execute("""
            SELECT con.id_consulta, c.id_veterinario, c.estado
            FROM consulta con
            INNER JOIN atencion a ON a.id_atencion = con.id_atencion
            INNER JOIN cita c ON c.id_cita = a.id_cita
            WHERE con.id_consulta = %s
        """, (id_consulta,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if con and con.is_connected(): con.close()


def _contexto(cursor,id_consulta,id_veterinario):
    cursor.execute("SELECT con.id_consulta,c.id_veterinario,c.estado FROM consulta con INNER JOIN atencion a ON a.id_atencion=con.id_atencion INNER JOIN cita c ON c.id_cita=a.id_cita WHERE con.id_consulta=%s FOR UPDATE",(id_consulta,))
    fila=cursor.fetchone()
    if fila is None: raise LookupError("Consulta no encontrada")
    if fila['id_veterinario']!=id_veterinario: raise PermissionError("No tienes permisos sobre esta consulta")
    if fila['estado']!='EN_ATENCION': raise ValueError("La cita debe estar EN_ATENCION")

def listar_recetas(id_consulta):
    con=cur=None
    try:
        con=get_connection();cur=con.cursor(dictionary=True);cur.execute("SELECT id_receta,id_consulta,fecha_emision,indicaciones FROM receta WHERE id_consulta=%s ORDER BY id_receta",(id_consulta,));return cur.fetchall()
    finally:
        if cur:cur.close()
        if con and con.is_connected():con.close()

def registrar_receta(id_consulta,id_veterinario,datos):
    con=cur=None
    try:
        con=get_connection();con.start_transaction();cur=con.cursor(dictionary=True);_contexto(cur,id_consulta,id_veterinario);cur.execute("INSERT INTO receta (id_consulta,indicaciones) VALUES (%s,%s)",(id_consulta,datos.indicaciones));rid=cur.lastrowid;con.commit();return rid
    except Exception:
        if con and con.is_connected():con.rollback()
        raise
    finally:
        if cur:cur.close()
        if con and con.is_connected():con.close()

def actualizar_receta(id_receta,id_veterinario,datos,id_consulta_esperada=None):
    campos=datos.model_dump(exclude_unset=True)
    if not campos: raise ValueError("Debe proporcionar al menos un campo para actualizar")
    con=cur=None
    try:
        con=get_connection();con.start_transaction();cur=con.cursor(dictionary=True);cur.execute("SELECT r.id_receta,r.id_consulta FROM receta r WHERE r.id_receta=%s FOR UPDATE",(id_receta,));r=cur.fetchone()
        if r is None:raise LookupError("Receta no encontrada")
        if id_consulta_esperada is not None and r['id_consulta'] != id_consulta_esperada: raise PermissionError("La receta no pertenece a la consulta indicada")
        _contexto(cur,r['id_consulta'],id_veterinario);cur.execute("UPDATE receta SET indicaciones=%s WHERE id_receta=%s",(campos['indicaciones'],id_receta));con.commit();return True
    except Exception:
        if con and con.is_connected():con.rollback()
        raise
    finally:
        if cur:cur.close()
        if con and con.is_connected():con.close()
