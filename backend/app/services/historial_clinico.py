from backend.app.repositories import historial_clinico as repo
def contexto(i):return repo.contexto_mascota(i)
def veterinario_autorizado(m,v):return repo.veterinario_tiene_cita(m,v)
def obtener(i,id_atencion=None):
 filas=repo.resumen(i,id_atencion);ids=[f['id_atencion'] for f in filas];rs=repo.recetas(ids);ds=repo.detalles([r['id_receta'] for r in rs]);vs=repo.vacunas(ids);por_a={a['id_atencion']:{**a,'recetas':[],'vacunas':[]} for a in filas};por_r={r['id_receta']:{**r,'detalles':[]} for r in rs}
 for d in ds:
  if d['id_receta'] in por_r:por_r[d['id_receta']]['detalles'].append(d)
 for r in por_r.values():
  if r['id_atencion'] in por_a:por_a[r['id_atencion']]['recetas'].append(r)
 for v in vs:
  if v['id_atencion'] in por_a:por_a[v['id_atencion']]['vacunas'].append(v)
 return list(por_a.values())
