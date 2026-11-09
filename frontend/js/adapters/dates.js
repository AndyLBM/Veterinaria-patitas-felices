// No se interpreta un DATETIME civil de Lima como UTC ni se añade "Z".
export function formatLocalDateTime(value) {
  if (typeof value !== 'string') return 'Sin fecha';
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::\d{2})?$/.exec(value);
  if (!match) return 'Formato de fecha no disponible';
  const [, year, month, day, hour, minute] = match;
  return `${day}/${month}/${year} · ${hour}:${minute}`;
}
