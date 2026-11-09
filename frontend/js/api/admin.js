import { http } from '../core/http.js';
import { ADMIN_MODULES, adminPayload } from '../adapters/admin.js';
export function createAdminApi(client = http) {
  const config = key => { const module = ADMIN_MODULES[key]; if (!module) throw new TypeError('Módulo administrativo no válido.'); return module; };
  const id = value => { if (!Number.isSafeInteger(value) || value <= 0) throw new TypeError('Identificador no válido.'); return value; };
  return Object.freeze({
    list(key, options) { return client.get(`${config(key).endpoint}/`, options); },
    get(key, value, options) { return client.get(`${config(key).endpoint}/${id(value)}`, options); },
    create(key, values, options) {
      const m = config(key); if (!m.create) throw new TypeError('Alta no disponible.');
      return client.post(key === 'clientes' ? 'clientes/registro' : `${m.endpoint}/`, adminPayload(key, values, true), key === 'clientes' ? { ...options, auth: false } : options);
    },
    update(key, value, values, options) {
      const m = config(key); if (!m.edit) throw new TypeError('Edición no disponible.');
      return client.put(`${m.endpoint}/${id(value)}`, adminPayload(key, values), options);
    },
    setState(key, record, state, options) {
      const m = config(key); if (!m.state || !['ACTIVO', 'INACTIVO'].includes(state)) throw new TypeError('Estado no válido.');
      const endpoint = key === 'clientes' ? 'usuarios' : m.endpoint;
      const value = key === 'clientes' ? record.id_usuario : record[m.pk];
      return client.patch(`${endpoint}/${id(value)}/estado`, { estado: state }, options);
    },
  });
}
export const adminApi = createAdminApi();
