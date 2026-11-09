import { http } from '../core/http.js';
import { clinicalPayload, agendaQuery } from '../adapters/clinical.js';
function id(value) { if (!Number.isSafeInteger(value) || value <= 0) throw new TypeError('Identificador no válido.'); return value; }
function path(kind, ctx, record) {
  if (kind === 'atencion') { if (record) throw new TypeError('La atención no tiene edición.'); return 'atenciones/'; }
  if (['triaje', 'consulta'].includes(kind)) return `atenciones/${id(ctx.id_atencion)}/${kind}/`;
  if (kind === 'receta') return `consultas/${id(ctx.id_consulta)}/recetas/${record ? id(record.id_receta) : ''}`;
  if (kind === 'detalle') return `recetas/${id(ctx.id_receta)}/detalles/${record ? id(record.id_detalle) : ''}`;
  if (kind === 'vacuna') return `consultas/${id(ctx.id_consulta)}/vacunas/${record ? id(record.id_vacuna) : ''}`;
  throw new TypeError('Recurso no válido.');
}
export function createClinicalApi(client = http) {
  return Object.freeze({
    agenda: (query = {}, options) => client.get('citas/mi-agenda', { ...options, query: agendaQuery(query) }),
    appointment: (value, options) => client.get(`citas/${id(value)}`, options),
    attention: (value, options) => client.get(`citas/${id(value)}/atencion`, options),
    triage: (value, options) => client.get(`atenciones/${id(value)}/triaje/`, options),
    consultation: (value, options) => client.get(`atenciones/${id(value)}/consulta/`, options),
    prescriptions: (value, options) => client.get(`consultas/${id(value)}/recetas/`, options),
    details: (value, options) => client.get(`recetas/${id(value)}/detalles/`, options),
    vaccines: (value, options) => client.get(`consultas/${id(value)}/vacunas/`, options),
    changeState(value, state, options) { if (!['CONFIRMADA', 'EN_ATENCION', 'ATENDIDA'].includes(state)) throw new TypeError('Transición no ofrecida.'); return client.patch(`citas/${id(value)}/estado`, { estado: state }, options); },
    save(kind, ctx, values, record, options) {
      const body = clinicalPayload(kind, values);
      if (kind === 'atencion') body.id_cita = id(ctx.id_cita);
      return client[record ? 'put' : 'post'](path(kind, ctx, record), body, options);
    },
  });
}
export const clinicalApi = createClinicalApi();
