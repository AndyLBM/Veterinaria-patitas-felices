import { checkApi } from '../api/status.js';
import { API_BASE_URL } from '../config.js';
import { errorMessage } from '../core/errors.js';
import { withBusy } from '../components/buttons.js';
import { state } from '../components/states.js';

export function mountConnection({ host, signal }) {
  const result = host.querySelector('[data-connection-result]');
  host.querySelector('[data-api-base]').textContent = API_BASE_URL;
  host.querySelector('[data-check-api]').addEventListener('click', event => withBusy(event.currentTarget, async () => {
    result.replaceChildren(state({ kind: 'loading', title: 'Comprobando conexión…', message: 'Se envía una consulta GET al estado de la API.' }));
    try {
      const data = await checkApi({ signal });
      if (!data || typeof data.mensaje !== 'string') throw new Error('Respuesta de API inesperada');
      if (!signal.aborted) result.replaceChildren(state({ title: 'FastAPI respondió correctamente', message: data.mensaje }));
    } catch (error) {
      if (!signal.aborted) result.replaceChildren(state({ kind: 'error', title: 'No se pudo verificar la API', message: errorMessage(error) }));
    }
  }), { signal });
}
