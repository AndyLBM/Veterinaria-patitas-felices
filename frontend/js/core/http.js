import { API_BASE_URL } from '../config.js';
import { getAccessToken, clearSession, onSessionChange } from './session.js';
import { ApiError, responseError } from './errors.js';

export function createHttpClient({ baseUrl = API_BASE_URL, fetchImpl = (...args) => globalThis.fetch(...args), tokenProvider = getAccessToken, onUnauthorized = () => clearSession('expired'), timeoutMs = 15000 } = {}) {
  const origin = globalThis.location?.origin || 'http://localhost';
  const base = new URL(baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`, origin);
  if (!['http:', 'https:'].includes(base.protocol) || base.search || base.hash || base.username || base.password) throw new TypeError('URL base de API no válida.');
  const pendingWrites = new Map();
  const controllers = new Set();

  async function request(method, path = '', { body, query, signal, auth = true, accessToken, invalidateSession = true, headers: customHeaders = {} } = {}) {
    if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(path)) throw new ApiError('Usa una ruta relativa a la API.', { code: 'INVALID_URL' });
    const url = new URL(path.replace(/^\//, ''), base);
    if (url.origin !== base.origin || !url.pathname.startsWith(base.pathname)) throw new ApiError('La ruta está fuera de la API configurada.', { code: 'INVALID_URL' });
    if (query) for (const [key, value] of Object.entries(query)) if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, String(value));
    const encodedBody = body === undefined ? undefined : JSON.stringify(body);
    const isWrite = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
    const requestKey = `${method} ${url.href} ${encodedBody ?? ''}`;
    if (isWrite && pendingWrites.has(requestKey)) throw new ApiError('Esta solicitud ya está en curso.', { code: 'DUPLICATE_REQUEST' });
    if (signal?.aborted) throw new ApiError('Solicitud cancelada.', { code: 'ABORTED' });

    const headers = new Headers(customHeaders);
    headers.set('Accept', 'application/json');
    if (encodedBody !== undefined) headers.set('Content-Type', 'application/json');
    // Authorization solo procede del proveedor en memoria, nunca de la URL.
    headers.delete('Authorization');
    const token = auth ? (accessToken ?? tokenProvider()) : null;
    if (token) headers.set('Authorization', `Bearer ${token}`);
    const controller = new AbortController();
    controllers.add(controller);
    let timedOut = false;
    const abort = () => controller.abort();
    signal?.addEventListener('abort', abort, { once: true });
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs);
    if (isWrite) pendingWrites.set(requestKey, controller);
    try {
      const response = await fetchImpl(url.href, { method, headers, body: encodedBody, signal: controller.signal, credentials: 'omit' });
      if (response.status === 204) return null;
      const text = await response.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch {
        if (response.ok) throw new ApiError('La API no devolvió una respuesta JSON válida. Revisa el proxy /api/.', { status: response.status, code: 'INVALID_RESPONSE' });
      }
      if (!response.ok) {
        const error = responseError(response.status, data);
        if (response.status === 401 && auth && invalidateSession && accessToken === undefined && token === tokenProvider()) onUnauthorized();
        throw error;
      }
      return data;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (timedOut) throw new ApiError('La conexión tardó demasiado. Inténtalo nuevamente.', { code: 'TIMEOUT', cause: error });
      if (controller.signal.aborted) throw new ApiError('Solicitud cancelada.', { code: 'ABORTED', cause: error });
      throw new ApiError('No se pudo conectar con la API. Revisa FastAPI y el proxy /api/.', { code: 'NETWORK_ERROR', cause: error });
    } finally {
      clearTimeout(timer);
      controllers.delete(controller);
      signal?.removeEventListener('abort', abort);
      if (isWrite && pendingWrites.get(requestKey) === controller) pendingWrites.delete(requestKey);
    }
  }

  return Object.freeze({
    cancelAll() { for (const controller of controllers) controller.abort(); pendingWrites.clear(); },
    get: (path, options) => request('GET', path, options),
    post: (path, body, options) => request('POST', path, { ...options, body }),
    put: (path, body, options) => request('PUT', path, { ...options, body }),
    patch: (path, body, options) => request('PATCH', path, { ...options, body }),
    delete: (path, options) => request('DELETE', path, options),
  });
}

export const http = createHttpClient();
onSessionChange(session => { if (!session) http.cancelAll(); });
