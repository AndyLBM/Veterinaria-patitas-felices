import { routes, resolveRoute } from './routes.js';
import { getSession, onSessionChange } from './session.js';
import { canAccess } from './guards.js';
import { state } from '../components/states.js';
import { hydrateIcons } from '../components/icons.js';

export function startRouter({ host, onNavigate, mount }) {
  let controller;
  let currentCleanup;
  async function navigate() {
    controller?.abort(); currentCleanup?.(); currentCleanup = null;
    controller = new AbortController();
    const { signal } = controller;
    const requested = resolveRoute(window.location.hash);
    const session = getSession();
    const allowed = canAccess(requested, session);
    const route = allowed ? requested : routes.find(item => item.page === 'denied');
    if (!allowed) history.replaceState(null, '', '#/acceso-denegado');
    // La autorización se evalúa antes de descargar o montar la vista protegida.
    onNavigate(route, session);
    document.getElementById('main-content').setAttribute('aria-busy', 'true');
    host.replaceChildren(state({ kind: 'loading', title: 'Preparando tu espacio…', message: 'Cargando la vista.' }));
    try {
      const response = await fetch(new URL(`../../views/${route.view}`, import.meta.url), { signal });
      if (!response.ok) throw new Error('Vista no disponible');
      const html = await response.text();
      if (signal.aborted) return;
      // Exclusivamente plantillas locales del catálogo constante routes.
      host.innerHTML = html;
      hydrateIcons(host);
      currentCleanup = await mount(route.page, { host, route, requested, session, signal });
      if (signal.aborted) { currentCleanup?.(); return; }
      document.title = `Patitas Felices · ${route.title}`;
      const heading = host.querySelector('h1');
      if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
      window.scrollTo({ top: 0, behavior: 'instant' });
    } catch (error) {
      if (signal.aborted) return;
      host.replaceChildren(state({ kind: 'error', title: 'No pudimos abrir esta página', message: 'Revisa la conexión y que los archivos del frontend estén disponibles.', action: { label: 'Reintentar', onClick: navigate } }));
    } finally {
      if (!signal.aborted) document.getElementById('main-content').setAttribute('aria-busy', 'false');
    }
  }
  window.addEventListener('hashchange', navigate);
  const unsubscribe = onSessionChange(session => {
    const current = resolveRoute(window.location.hash);
    if (current.roles) {
      if (!session) history.replaceState(null, '', '#/acceso');
      navigate();
    } else onNavigate(current, session);
  });
  navigate();
  return () => { controller?.abort(); currentCleanup?.(); unsubscribe(); window.removeEventListener('hashchange', navigate); };
}
