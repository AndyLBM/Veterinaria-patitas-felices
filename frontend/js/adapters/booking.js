import { seconds } from './agenda.js';
export function startCivil(date, time) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date || '') || !Number.isFinite(seconds(time))) throw new TypeError('Revisa fecha y hora.');
  return `${date}T${time.length === 5 ? time + ':00' : time}`;
}
// Aritmética de horas civiles, solo para presentar y validar dentro de la franja
// devuelta por FastAPI. Nunca convertir la fecha a la zona del equipo ni enviar fin.
export function endCivil(start, minutes) {
  const total = seconds(start?.slice(11)) + Number(minutes) * 60;
  if (!Number.isInteger(total) || Number(minutes) <= 0 || total >= 86400) return null;
  const h = n => String(n).padStart(2, '0');
  return `${start.slice(0, 10)}T${h(Math.floor(total / 3600))}:${h(Math.floor(total % 3600 / 60))}:${h(total % 60)}`;
}
export function fitsAvailability(data, start) {
  if (data?.zona_horaria !== 'America/Lima' || data?.fecha !== start?.slice(0, 10)) return false;
  const end = endCivil(start, data.duracion_minutos);
  return Boolean(end && data.franjas_disponibles?.some(f => start >= f.inicio && end <= f.fin));
}
export function reservationPayload(values) {
  const body = { id_mascota: Number(values.id_mascota), id_servicio: Number(values.id_servicio), id_veterinario: Number(values.id_veterinario), fecha_inicio: values.fecha_inicio, motivo: String(values.motivo || '').trim() || null };
  for (const key of ['id_mascota', 'id_servicio', 'id_veterinario']) if (!Number.isSafeInteger(body[key]) || body[key] <= 0) throw new TypeError('Selección no válida.');
  return body;
}
export function filterOwnAppointments(rows, values) {
  return rows.filter(r => (!values.estado || r.estado === values.estado) && (!values.fecha_desde || r.fecha_inicio.slice(0, 10) >= values.fecha_desde) && (!values.fecha_hasta || r.fecha_inicio.slice(0, 10) <= values.fecha_hasta));
}
