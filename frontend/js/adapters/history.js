// IDs y relaciones de la respuesta real; nunca se deduplica por nombres clínicos.
export function historyId(value) {
  if (!Number.isSafeInteger(value) || value <= 0) throw new TypeError('Identificador de historial no válido.');
  return value;
}
function unique(rows, key) {
  if (!Array.isArray(rows)) throw new TypeError('Respuesta de historial no válida.');
  return [...new Map(rows.map(row => [historyId(row[key]), row])).values()];
}
function linked(actual, expected) {
  if (actual !== expected) throw new TypeError('La respuesta clínica no corresponde a la mascota seleccionada.');
}
export function normalizeAttention(record, pet) {
  historyId(record.id_atencion); linked(record.id_mascota, historyId(pet));
  const recipes = unique(record.recetas, 'id_receta').map(recipe => {
    linked(recipe.id_atencion, record.id_atencion);
    const details = unique(recipe.detalles, 'id_detalle');
    for (const item of details) linked(item.id_receta, recipe.id_receta);
    return { ...recipe, detalles: details };
  });
  const vaccines = unique(record.vacunas, 'id_vacuna');
  for (const vaccine of vaccines) linked(vaccine.id_atencion, record.id_atencion);
  return { ...record, recetas: recipes, vacunas: vaccines };
}
export function normalizeHistory(response, pet) {
  linked(response.mascota?.id_mascota, historyId(pet));
  return { mascota: response.mascota, atenciones: unique(response.atenciones, 'id_atencion')
    .map(row => normalizeAttention(row, pet))
    // DATETIME civil de Lima: ordenar sin convertir a UTC ni a la zona del navegador.
    .sort((a, b) => String(b.fecha_atencion).localeCompare(String(a.fecha_atencion)) || b.id_atencion - a.id_atencion) };
}
export function historyPetOptions(role, rows) {
  if (![1, 2, 3].includes(role)) throw new TypeError('Rol no válido.');
  return unique(rows, 'id_mascota').map(row => ({ id_mascota: row.id_mascota,
    nombre: role === 2 ? row.nombre_mascota : row.nombre,
    especie: role === 2 ? row.especie_mascota : row.especie,
  })).sort((a, b) => String(a.nombre).localeCompare(String(b.nombre), 'es'));
}
