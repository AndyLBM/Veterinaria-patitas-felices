import { http } from '../core/http.js';
import { historyId, historyPetOptions, normalizeHistory, normalizeAttention } from '../adapters/history.js';
export function createHistoryApi(client = http) {
  return Object.freeze({
    async pets(role, options) {
      if (![1, 2, 3].includes(role)) throw new TypeError('Rol no válido.');
      const rows = await client.get(role === 2 ? 'citas/mi-agenda' : 'mascotas/', options);
      return historyPetOptions(role, rows);
    },
    async list(pet, options) {
      const response = await client.get(`mascotas/${historyId(pet)}/historial-clinico/`, options);
      return normalizeHistory(response, pet);
    },
    async detail(pet, attention, options) {
      const response = await client.get(`mascotas/${historyId(pet)}/historial-clinico/${historyId(attention)}`, options);
      if (response.mascota?.id_mascota !== pet || response.atencion?.id_atencion !== attention) throw new TypeError('La respuesta no corresponde a la atención solicitada.');
      return normalizeAttention(response.atencion, pet);
    },
  });
}
export const historyApi = createHistoryApi();
