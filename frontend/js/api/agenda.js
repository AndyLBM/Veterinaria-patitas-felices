import { http } from '../core/http.js';
import { schedulePayload, appointmentQuery, APPOINTMENT_STATES } from '../adapters/agenda.js';
function id(value) { if (!Number.isSafeInteger(value) || value <= 0) throw new TypeError('Identificador no válido.'); return value; }
export function createAgendaApi(client = http) {
  return Object.freeze({
    schedules(vet, options) { return client.get('horarios-veterinarios/', { ...options, query: vet ? { id_veterinario: id(Number(vet)) } : {} }); },
    schedule(value, options) { return client.get(`horarios-veterinarios/${id(value)}`, options); },
    createSchedule(values, options) { return client.post('horarios-veterinarios/', schedulePayload(values, true), options); },
    updateSchedule(value, values, options) { return client.put(`horarios-veterinarios/${id(value)}`, schedulePayload(values), options); },
    appointments(query = {}, options) { return client.get('citas/', { ...options, query: appointmentQuery(query) }); },
    appointment(value, options) { return client.get(`citas/${id(value)}`, options); },
    changeState(value, state, options) { if (!Object.hasOwn(APPOINTMENT_STATES, state)) throw new TypeError('Estado no válido.'); return client.patch(`citas/${id(value)}/estado`, { estado: state }, options); },
  });
}
export const agendaApi = createAgendaApi();
