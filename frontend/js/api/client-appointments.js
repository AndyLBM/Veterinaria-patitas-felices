import { http } from '../core/http.js';
import { reservationPayload } from '../adapters/booking.js';
function id(value) { if (!Number.isSafeInteger(value) || value <= 0) throw new TypeError('Identificador no válido.'); return value; }
export function createClientAppointmentsApi(client = http) {
  return Object.freeze({
    services: options => client.get('citas/servicios-disponibles', options),
    vets: (service, date, options) => client.get('citas/veterinarios-disponibles', { ...options, query: { id_servicio: id(Number(service)), fecha: date } }),
    availability: (vet, service, date, options) => client.get('citas/disponibilidad', { ...options, query: { id_veterinario: id(Number(vet)), id_servicio: id(Number(service)), fecha: date } }),
    create: (values, options) => client.post('citas/', reservationPayload(values), options),
    list: options => client.get('citas/mis-citas', options),
    get: (value, options) => client.get(`citas/${id(value)}`, options),
    reprogramAvailability: (value, vet, date, options) => client.get(`citas/${id(value)}/disponibilidad-reprogramacion`, { ...options, query: { id_veterinario: id(Number(vet)), fecha: date } }),
    reprogram: (value, values, options) => client.patch(`citas/${id(value)}/reprogramacion`, { id_veterinario: id(Number(values.id_veterinario)), fecha_inicio: values.fecha_inicio }, options),
    cancel: (value, options) => client.patch(`citas/${id(value)}/cancelacion`, undefined, options),
  });
}
export const clientAppointmentsApi = createClientAppointmentsApi();
