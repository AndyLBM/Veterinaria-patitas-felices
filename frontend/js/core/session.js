// Memoria exclusivamente. Solo instalar después de verificar /auth/me.
let session = null;
let revision = 0;
let expiryTimer;
const listeners = new Set();

export function getSession() { return session; }
export function getAccessToken() { return session?.accessToken ?? null; }
export function getSessionRevision() { return revision; }
export function tokenExpiresAt(token) {
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(part.padEnd(Math.ceil(part.length / 4) * 4, '=')));
    return typeof payload.exp === 'number' && Number.isFinite(payload.exp) ? payload.exp * 1000 : null;
  } catch { return null; }
}
export function clearSession(reason = 'logout') {
  const hadSession = Boolean(session);
  clearTimeout(expiryTimer);
  session = null;
  revision++;
  for (const listener of listeners) listener(null, { reason, hadSession });
}
export function checkSessionExpiration() {
  if (!session) return;
  if (session.expiresAt <= Date.now()) { clearSession('expired'); return; }
  clearTimeout(expiryTimer);
  expiryTimer = setTimeout(checkSessionExpiration, Math.min(session.expiresAt - Date.now(), 2147483647));
  expiryTimer.unref?.();
}
export function setVerifiedSession({ accessToken, user, profile, expiresAt = tokenExpiresAt(accessToken ?? '') }) {
  // Usar solo después de verificar la identidad con FastAPI. El navegador no
  // valida la firma del JWT y nunca sustituye la autorización del servidor.
  if (typeof accessToken !== 'string' || !accessToken.trim() || ![1, 2, 3].includes(user?.id_rol) || !Number.isInteger(user?.id_usuario) || user.id_usuario <= 0 || !Number.isFinite(expiresAt) || expiresAt <= Date.now()) {
    throw new TypeError('La sesión requiere una identidad verificada por el backend.');
  }
  // Identidad mínima de autorización y, para roles 2/3, presentación del login
  // verificado. Nunca copiar la respuesta completa, contraseñas o id_cliente.
  const presentation = [2, 3].includes(user.id_rol) && profile ? Object.freeze(Object.fromEntries(
    [['nombre', 80], ['apellido', 80], ['correo', 150]].filter(([key, max]) => typeof profile[key] === 'string' && [...profile[key]].length <= max).map(([key]) => [key, profile[key]])
  )) : null;
  session = Object.freeze({ accessToken, expiresAt, user: Object.freeze({ id_usuario: user.id_usuario, id_rol: user.id_rol }), ...(presentation ? { profile: presentation } : {}) });
  revision++;
  checkSessionExpiration();
  for (const listener of listeners) listener(session, { reason: 'login' });
}
export function onSessionChange(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
