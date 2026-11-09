import { http } from '../core/http.js';
import { ApiError } from '../core/errors.js';
import { getSessionRevision, setVerifiedSession, tokenExpiresAt } from '../core/session.js';

export const ROLE_HOME = Object.freeze({ 1: '/admin/panel', 2: '/veterinario/panel', 3: '/cliente/panel' });
const invalidResponse = () => new ApiError('La respuesta de autenticación no es válida. Inténtalo nuevamente.', { code: 'INVALID_RESPONSE' });

export function createAuthService({ client = http, installSession = setVerifiedSession, readRevision = getSessionRevision } = {}) {
  return Object.freeze({
    async login({ correo, password }, { signal } = {}) {
      const revision = readRevision();
      let result;
      try { result = await client.post('auth/login', { correo, password }, { auth: false, signal }); }
      catch (error) {
        if (error.status === 401) throw new ApiError('Correo o contraseña incorrectos.', { status: 401, code: 'INVALID_CREDENTIALS' });
        throw error;
      }
      if (typeof result?.access_token !== 'string' || typeof result.token_type !== 'string' || result.token_type.toLowerCase() !== 'bearer' || !Number.isInteger(result.usuario?.id_usuario)) throw invalidResponse();
      // El token candidato no se instala como sesión antes de /auth/me.
      let identity;
      try { identity = await client.get('auth/me', { accessToken: result.access_token, invalidateSession: false, signal }); }
      catch (error) {
        if (error.status === 401) throw new ApiError('No se pudo verificar la sesión. Inicia sesión nuevamente.', { status: 401, code: 'UNVERIFIED_SESSION' });
        throw error;
      }
      if (identity?.id_usuario !== result.usuario.id_usuario || !ROLE_HOME[identity?.id_rol] || !Number.isInteger(identity.id_rol)) throw invalidResponse();
      const expiresAt = tokenExpiresAt(result.access_token);
      if (expiresAt === null || expiresAt <= Date.now()) throw new ApiError('El acceso ha vencido. Inicia sesión nuevamente.', { status: 401, code: 'EXPIRED_TOKEN' });
      if (signal?.aborted || readRevision() !== revision) throw new ApiError('Solicitud cancelada.', { code: 'ABORTED' });
      installSession({ accessToken: result.access_token, user: identity, expiresAt, profile: [2, 3].includes(identity.id_rol) ? result.usuario : undefined });
      return ROLE_HOME[identity.id_rol];
    },
    async register({ nombre, apellido, correo, password, telefono }, { signal } = {}) {
      // Lista cerrada: ningún rol o identificador recibido se envía a la API.
      const body = { nombre, apellido, correo, password };
      if (telefono) body.telefono = telefono;
      const result = await client.post('clientes/registro', body, { auth: false, signal });
      if (!Number.isInteger(result?.id_cliente) || result.id_cliente <= 0) throw invalidResponse();
      return { id_cliente: result.id_cliente };
    },
  });
}
export const auth = createAuthService();
