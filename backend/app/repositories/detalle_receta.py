from backend.app.database.connection import get_connection


def obtener_contexto_receta(id_receta):
 con=cur=None
 try:
  con=get_connection();cur=con.cursor(dictionary=True)
  cur.execute("""SELECT r.id_receta,c.id_veterinario,c.estado
                 FROM receta r INNER JOIN consulta con ON con.id_consulta=r.id_consulta
                 INNER JOIN atencion a ON a.id_atencion=con.id_atencion
                 INNER JOIN cita c ON c.id_cita=a.id_cita
                 WHERE r.id_receta=%s""",(id_receta,))
  return cur.fetchone()
 finally:
  if cur:cur.close()
  if con and con.is_connected():con.close()


def _contexto(cursor,id_receta,id_veterinario):
    cursor.execute("SELECT r.id_receta,c.id_veterinario,c.estado FROM receta r INNER JOIN consulta con ON con.id_consulta=r.id_consulta INNER JOIN atencion a ON a.id_atencion=con.id_atencion INNER JOIN cita c ON c.id_cita=a.id_cita WHERE r.id_receta=%s FOR UPDATE",(id_receta,));fila=cursor.fetchone()
    if fila is None:raise LookupError("Receta no encontrada")
    if fila['id_veterinario']!=id_veterinario:raise PermissionError("No tienes permisos sobre esta receta")
    if fila['estado']!='EN_ATENCION':raise ValueError("La cita debe estar EN_ATENCION")

def listar_detalles(id_receta):
    con=cur=None
    try:
        con=get_connection();cur=con.cursor(dictionary=True);cur.execute("SELECT id_detalle,id_receta,medicamento,dosis,frecuencia,duracion,indicaciones FROM detalle_receta WHERE id_receta=%s ORDER BY id_detalle",(id_receta,));return cur.fetchall()
    finally:
        if cur:cur.close()
        if con and con.is_connected():con.close()

def registrar_detalle(id_receta,id_veterinario,datos):
    con=cur=None
    try:
        con=get_connection();con.start_transaction();cur=con.cursor(dictionary=True);_contexto(cur,id_receta,id_veterinario);cur.execute("INSERT INTO detalle_receta (id_receta,medicamento,dosis,frecuencia,duracion,indicaciones) VALUES (%s,%s,%s,%s,%s,%s)",(id_receta,datos.medicamento,datos.dosis,datos.frecuencia,datos.duracion,datos.indicaciones));x=cur.lastrowid;con.commit();return x
    except Exception:
        if con and con.is_connected():con.rollback()
        raise
    finally:
        if cur:cur.close()
        if con and con.is_connected():con.close()

def actualizar_detalle(id_detalle,id_veterinario,datos,id_receta_esperada=None):
    campos=datos.model_dump(exclude_unset=True)
    if not campos:raise ValueError("Debe proporcionar al menos un campo para actualizar")
    con=cur=None
    try:
        con=get_connection();con.start_transaction();cur=con.cursor(dictionary=True);cur.execute("SELECT id_detalle,id_receta FROM detalle_receta WHERE id_detalle=%s FOR UPDATE",(id_detalle,));d=cur.fetchone()
        if d is None:raise LookupError("Detalle de receta no encontrado")
        if id_receta_esperada is not None and d['id_receta'] != id_receta_esperada:raise PermissionError("El detalle no pertenece a la receta indicada")
        _contexto(cur,d['id_receta'],id_veterinario);asig=', '.join(f'{k}=%s' for k in campos);cur.execute(f"UPDATE detalle_receta SET {asig} WHERE id_detalle=%s",tuple([*campos.values(),id_detalle]));con.commit();return True
    except Exception:
        if con and con.is_connected():con.rollback()
        raise
    finally:
        if cur:cur.close()
        if con and con.is_connected():con.close()
