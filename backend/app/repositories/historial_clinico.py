from backend.app.database.connection import get_connection

def contexto_mascota(id_mascota):
 c=x=None
 try:
  c=get_connection();x=c.cursor(dictionary=True);x.execute("SELECT m.id_mascota,m.id_cliente,m.nombre,m.especie,m.raza FROM mascota m WHERE m.id_mascota=%s",(id_mascota,));return x.fetchone()
 finally:
  if x:x.close()
  if c and c.is_connected():c.close()
def veterinario_tiene_cita(id_mascota,id_veterinario):
 c=x=None
 try:
  c=get_connection();x=c.cursor();x.execute("SELECT id_cita FROM cita WHERE id_mascota=%s AND id_veterinario=%s LIMIT 1",(id_mascota,id_veterinario));return x.fetchone() is not None
 finally:
  if x:x.close()
  if c and c.is_connected():c.close()
def resumen(id_mascota,id_atencion=None):
 c=x=None
 try:
  c=get_connection();x=c.cursor(dictionary=True);q="SELECT * FROM vw_historial_clinico WHERE id_mascota=%s";p=[id_mascota]
  if id_atencion is not None:q+=" AND id_atencion=%s";p.append(id_atencion)
  x.execute(q+" ORDER BY fecha_atencion DESC",tuple(p));return x.fetchall()
 finally:
  if x:x.close()
  if c and c.is_connected():c.close()
def recetas(ids):
 if not ids:return []
 c=x=None
 try:
  c=get_connection();x=c.cursor(dictionary=True);m=', '.join(['%s']*len(ids));x.execute(f"SELECT r.id_receta,r.id_consulta,con.id_atencion,r.fecha_emision,r.indicaciones FROM receta r INNER JOIN consulta con ON con.id_consulta=r.id_consulta WHERE con.id_atencion IN ({m})",tuple(ids));return x.fetchall()
 finally:
  if x:x.close()
  if c and c.is_connected():c.close()
def detalles(ids):
 if not ids:return []
 c=x=None
 try:
  c=get_connection();x=c.cursor(dictionary=True);m=', '.join(['%s']*len(ids));x.execute(f"SELECT id_detalle,id_receta,medicamento,dosis,frecuencia,duracion,indicaciones FROM detalle_receta WHERE id_receta IN ({m})",tuple(ids));return x.fetchall()
 finally:
  if x:x.close()
  if c and c.is_connected():c.close()
def vacunas(ids):
 if not ids:return []
 c=x=None
 try:
  c=get_connection();x=c.cursor(dictionary=True);m=', '.join(['%s']*len(ids));x.execute(f"SELECT id_vacuna,id_atencion,nombre_vacuna,fecha_aplicacion,proxima_dosis,observaciones FROM vacuna WHERE id_atencion IN ({m})",tuple(ids));return x.fetchall()
 finally:
  if x:x.close()
  if c and c.is_connected():c.close()
