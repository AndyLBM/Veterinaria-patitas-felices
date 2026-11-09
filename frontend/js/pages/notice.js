export function mountNotice(kind, { host, route, session }) {
  const content = {
    denied: [session ? 'No tienes acceso a esta área' : 'Este espacio requiere una sesión', session ? 'Tu rol no tiene permisos para abrir esta página.' : 'Inicia sesión para entrar al área que corresponda a tu cuenta. Si recargaste la página, necesitas identificarte nuevamente.', 'Acceso restringido'],
    notFound: ['No encontramos esta página', 'La dirección no corresponde a una pantalla de la plataforma. Puedes regresar al inicio o utilizar el menú.', 'Página no encontrada'],
    pending: [route.title, route.description + ' La pantalla está pendiente de implementación; no se han consultado ni cargado registros.', 'Pendiente de implementación'],
  }[kind];
  host.querySelector('[data-notice-title]').textContent = content[0];
  host.querySelector('[data-notice-message]').textContent = content[1];
  host.querySelector('[data-notice-badge]').textContent = content[2];
  const accessLink = host.querySelector('[data-access-link]');
  if (accessLink) accessLink.hidden = kind === 'access' || kind === 'notFound' || kind === 'pending';
}
