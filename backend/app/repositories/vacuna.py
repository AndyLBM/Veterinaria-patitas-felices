from backend.app.database.connection import get_connection

def obtener_contexto_consulta(id_consulta):
 con=cur=None
 try:
  con=get_connection();cur=con.cursor(dictionary=True);cur.execute("SELECT con.id_consulta,con.id_atencion,c.id_veterinario,m.id_cliente,c.estado FROM consulta con INNER JOIN atencion a ON a.id_atencion=con.id_atencion INNER JOIN cita c ON c.id_cita=a.id_cita INNER JOIN mascota m ON m.id_mascota=c.id_mascota WHERE con.id_consulta=%s",(id_consulta,));return cur.fetchone()
 finally:
  if cur:cur.close()
  if con and con.is_connected():con.close()
def _contexto(cursor,id_consulta,vet):
 cursor.execute("SELECT con.id_consulta,con.id_atencion,c.id_veterinario,c.estado FROM consulta con INNER JOIN atencion a ON a.id_atencion=con.id_atencion INNER JOIN cita c ON c.id_cita=a.id_cita WHERE con.id_consulta=%s FOR UPDATE",(id_consulta,));x=cursor.fetchone()
 if x is None:raise LookupError('Consulta no encontrada')
 if x['id_veterinario']!=vet:raise PermissionError('No tienes permisos sobre esta consulta')
 if x['estado']!='EN_ATENCION':raise ValueError('La cita debe estar EN_ATENCION')
 return x
def listar_vacunas(id_consulta):
 con=cur=None
 try:
  con=get_connection();cur=con.cursor(dictionary=True);cur.execute("SELECT v.id_vacuna,v.id_atencion,v.nombre_vacuna,v.fecha_aplicacion,v.proxima_dosis,v.observaciones FROM vacuna v INNER JOIN consulta con ON con.id_atencion=v.id_atencion WHERE con.id_consulta=%s ORDER BY v.id_vacuna",(id_consulta,));return cur.fetchall()
 finally:
  if cur:cur.close()
  if con and con.is_connected():con.close()
def registrar_vacuna(id_consulta,vet,datos):
 con=cur=None
 try:
  con=get_connection();con.start_transaction();cur=con.cursor(dictionary=True);ctx=_contexto(cur,id_consulta,vet);cur.execute("INSERT INTO vacuna (id_atencion,nombre_vacuna,fecha_aplicacion,proxima_dosis,observaciones) VALUES (%s,%s,%s,%s,%s)",(ctx['id_atencion'],datos.nombre_vacuna,datos.fecha_aplicacion,datos.proxima_dosis,datos.observaciones));i=cur.lastrowid;con.commit();return i
 except Exception:
  if con and con.is_connected():con.rollback()
  raise
 finally:
  if cur:cur.close()
  if con and con.is_connected():con.close()
def actualizar_vacuna(id_consulta,id_vacuna,vet,datos):
 con=cur=None
 try:
  con=get_connection();con.start_transaction();cur=con.cursor(dictionary=True);ctx=_contexto(cur,id_consulta,vet);cur.execute("SELECT id_vacuna,id_atencion FROM vacuna WHERE id_vacuna=%s FOR UPDATE",(id_vacuna,));v=cur.fetchone()
  if v is None:raise LookupError('Vacuna no encontrada')
  if v['id_atencion']!=ctx['id_atencion']:raise PermissionError('La vacuna no pertenece a la consulta indicada')
  cur.execute("UPDATE vacuna SET nombre_vacuna=%s,fecha_aplicacion=%s,proxima_dosis=%s,observaciones=%s WHERE id_vacuna=%s",(datos.nombre_vacuna,datos.fecha_aplicacion,datos.proxima_dosis,datos.observaciones,id_vacuna));con.commit();return True
 except Exception:
  if con and con.is_connected():con.rollback()
  raise
 finally:
  if cur:cur.close()
  if con and con.is_connected():con.close()
