export const WEEKDAYS = Object.freeze(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']);
export const APPOINTMENT_STATES = Object.freeze({ PROGRAMADA: 'Programada', CONFIRMADA: 'Confirmada', EN_ATENCION: 'En atención', ATENDIDA: 'Atendida', CANCELADA: 'Cancelada', NO_ASISTIO: 'No asistió' });
// Espejo del contrato de services/cita.py. FastAPI revalida cada transición.
export const TRANSITIONS = Object.freeze({ PROGRAMADA: ['CONFIRMADA', 'CANCELADA'], CONFIRMADA: ['EN_ATENCION', 'CANCELADA', 'NO_ASISTIO'], EN_ATENCION: ['ATENDIDA'], ATENDIDA: [], CANCELADA: [], NO_ASISTIO: [] });
export function seconds(value) {
  const match = /^(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(value || '');
  if (!match || +match[1] > 23 || +match[2] > 59 || +(match[3] || 0) > 59) return NaN;
  return +match[1] * 3600 + +match[2] * 60 + +(match[3] || 0);
}
export function validHours(start, end) { return Number.isFinite(seconds(start)) && seconds(start) < seconds(end); }
export function schedulePayload(values, creating = false) {
  const body = { dia_semana: Number(values.dia_semana), hora_inicio: values.hora_inicio, hora_fin: values.hora_fin };
  if (!Number.isInteger(body.dia_semana) || body.dia_semana < 1 || body.dia_semana > 7 || !validHours(body.hora_inicio, body.hora_fin)) throw new TypeError('Revisa el día y el rango de horas.');
  if (creating) { body.id_veterinario = Number(values.id_veterinario); if (!Number.isSafeInteger(body.id_veterinario) || body.id_veterinario <= 0) throw new TypeError('Selecciona un veterinario.'); }
  return body;
}
export function groupSchedules(rows) {
  const groups = new Map();
  for (const row of [...rows].sort((a, b) => a.id_veterinario - b.id_veterinario || a.dia_semana - b.dia_semana || seconds(a.hora_inicio) - seconds(b.hora_inicio))) {
    if (!groups.has(row.id_veterinario)) groups.set(row.id_veterinario, []);
    groups.get(row.id_veterinario).push(row);
  }
  return [...groups.values()];
}
export function appointmentQuery(values) {
  const query = {};
  for (const key of ['fecha_desde', 'fecha_hasta', 'estado', 'id_veterinario', 'id_cliente']) if (values[key]) query[key] = String(values[key]);
  if (query.fecha_desde && query.fecha_hasta && query.fecha_desde > query.fecha_hasta) throw new TypeError('La fecha inicial no puede ser posterior a la fecha final.');
  if (query.estado && !Object.hasOwn(APPOINTMENT_STATES, query.estado)) throw new TypeError('Estado no válido.');
  for (const key of ['id_veterinario', 'id_cliente']) if (query[key] && (!Number.isSafeInteger(Number(query[key])) || Number(query[key]) <= 0)) throw new TypeError('Identificador no válido.');
  return query;
}
export function limaNow(value = new Date()) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' }).formatToParts(value).map(p => [p.type, p.value]));
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}`;
}
export function upcomingAppointments(rows, now = limaNow()) { return rows.filter(r => ['PROGRAMADA', 'CONFIRMADA'].includes(r.estado) && r.fecha_inicio >= now).sort((a, b) => a.fecha_inicio.localeCompare(b.fecha_inicio) || a.id_cita - b.id_cita).slice(0, 5); }
export function dashboardSummary(key, rows) {
  const active = ['clientes', 'veterinarios', 'servicios'].includes(key);
  const count = active ? rows.filter(r => r.estado === 'ACTIVO').length : rows.length;
  return `${count} ${active ? count === 1 ? 'activo' : 'activos' : count === 1 ? 'registro' : 'registros'}`;
}
