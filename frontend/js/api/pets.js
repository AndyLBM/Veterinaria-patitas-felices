import { http } from '../core/http.js';
import { petPayload } from '../adapters/pets.js';
function id(value) { if (!Number.isSafeInteger(value) || value <= 0) throw new TypeError('Identificador no válido.'); return value; }
export function createPetsApi(client = http) {
  return Object.freeze({
    list: options => client.get('mascotas/', options),
    get: (value, options) => client.get(`mascotas/${id(value)}`, options),
    create: (values, options) => client.post('mascotas/', petPayload(values), options),
    update: (value, values, options) => client.put(`mascotas/${id(value)}`, petPayload(values), options),
    deactivate: (value, options) => client.delete(`mascotas/${id(value)}`, options),
  });
}
export const petsApi = createPetsApi();
