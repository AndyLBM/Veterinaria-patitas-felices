// Contratos explícitos. Nunca inferir campos editables a partir de una respuesta.
const person = [
  { name: 'nombre', label: 'Nombre', required: true, minLength: 2, maxLength: 80, autocomplete: 'given-name' },
  { name: 'apellido', label: 'Apellido', required: true, minLength: 2, maxLength: 80, autocomplete: 'family-name' },
  { name: 'correo', label: 'Correo electrónico', type: 'email', required: true, minLength: 5, maxLength: 150, autocomplete: 'email' },
  { name: 'telefono', label: 'Teléfono', type: 'tel', maxLength: 20 },
];
const password = { name: 'password', label: 'Contraseña inicial', type: 'password', required: true, minLength: 8, maxLength: 72, autocomplete: 'new-password', hint: 'De 8 a 72 caracteres; máximo 72 bytes UTF-8.' };
const catalog = [
  { name: 'nombre', label: 'Nombre', required: true, minLength: 2, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
];
const peopleColumns = [{ key: 'nombre', label: 'Nombre', format: (_, r) => `${r.nombre} ${r.apellido}` }, { key: 'correo', label: 'Correo electrónico' }];
export const ADMIN_MODULES = Object.freeze({
  cuentas: { title: 'Usuarios', singular: 'usuario', endpoint: 'usuarios', pk: 'id_usuario', note: 'Consulta las cuentas y administra su acceso. Los roles se muestran como información de solo lectura.', state: true, columns: [...peopleColumns, { key: 'rol', label: 'Rol' }] },
  clientes: { title: 'Clientes', singular: 'cliente', endpoint: 'clientes', pk: 'id_cliente', note: 'Este listado incluye únicamente clientes activos. Para reactivar una cuenta, abre Usuarios.', create: true, edit: true, state: true, fields: person, columns: peopleColumns },
  veterinarios: { title: 'Veterinarios', singular: 'veterinario', endpoint: 'veterinarios', pk: 'id_veterinario', note: 'Gestiona el equipo veterinario, sus datos de contacto y su especialidad.', create: true, edit: true, state: true, fields: [...person, { name: 'id_especialidad', label: 'Especialidad', type: 'select', required: true }, { name: 'numero_colegiatura', label: 'Número de colegiatura', required: true, minLength: 2, maxLength: 50 }], columns: [...peopleColumns, { key: 'especialidad', label: 'Especialidad' }] },
  especialidades: { title: 'Especialidades', singular: 'especialidad', endpoint: 'especialidades', pk: 'id_especialidad', note: 'Mantén el catálogo de especialidades del equipo veterinario.', create: true, edit: true, fields: catalog, columns: [{ key: 'nombre', label: 'Especialidad' }, { key: 'descripcion', label: 'Descripción' }] },
  servicios: { title: 'Servicios', singular: 'servicio', endpoint: 'servicios', pk: 'id_servicio', note: 'Administra los servicios, su duración y su precio. La duración vigente se aplica a nuevas citas.', create: true, edit: true, state: true, fields: [...catalog, { name: 'duracion_minutos', label: 'Duración (minutos)', type: 'number', required: true, min: 1, step: 1 }, { name: 'precio', label: 'Precio (opcional)', type: 'number', min: 0, max: '99999999.99', step: '0.01', hint: 'Hasta 8 cifras enteras y 2 decimales. Vacío: sin precio definido.' }], columns: [{ key: 'nombre', label: 'Servicio' }, { key: 'duracion_minutos', label: 'Duración', format: v => `${v} min` }, { key: 'precio', label: 'Precio', format: v => v == null ? 'Sin definir' : String(v) }] },
});
export function adminFields(key, creating = false) {
  const module = ADMIN_MODULES[key];
  if (!module || !(creating ? module.create : module.edit)) return [];
  return creating && ['clientes', 'veterinarios'].includes(key) ? [...module.fields, password] : [...module.fields];
}
export function adminPayload(key, values, creating = false) {
  const body = {};
  for (const f of adminFields(key, creating)) {
    let value = String(values[f.name] ?? '');
    if (f.name !== 'password') value = value.trim();
    if (!value && !f.required) value = null;
    if (['id_especialidad', 'duracion_minutos'].includes(f.name)) value = Number(value);
    body[f.name] = value;
  }
  return body;
}
export function matchingRecords(rows, query, state = '') {
  const term = query.trim().toLocaleLowerCase('es');
  return rows.filter(row => (!state || row.estado === state) && Object.entries(row).some(([key, v]) => key !== 'password_hash' && key !== 'password' && String(v ?? '').toLocaleLowerCase('es').includes(term)));
}
