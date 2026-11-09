import { routes } from '../core/routes.js';
import { icon } from './icons.js';

const PUBLIC = [
  { path: '/inicio', title: 'Bienvenida', iconName: 'home' },
  { path: '/componentes', title: 'Componentes', iconName: 'grid' },
  { path: '/conexion', title: 'Estado de conexión', iconName: 'server' },
];
const AREAS = [
  { path: '/admin/panel', title: 'Administración', iconName: 'users' },
  { path: '/veterinario/agenda', title: 'Espacio veterinario', iconName: 'calendar' },
  { path: '/cliente/mascotas', title: 'Espacio del cliente', iconName: 'heart' },
];

export function renderNavigation(host, activePath, session) {
  host.replaceChildren();
  const section = (label, items, locked = false) => {
    const title = document.createElement('p'); title.className = 'nav-section'; title.textContent = label;
    host.append(title);
    for (const item of items) {
      const link = document.createElement('a');
      link.className = 'nav-link'; link.href = `#${item.path}`;
      if (activePath === item.path) link.setAttribute('aria-current', 'page');
      link.append(icon(item.iconName || 'book'), document.createTextNode(item.title));
      if (locked) { const lock = icon('lock'); lock.classList.add('nav-lock'); link.append(lock); link.setAttribute('aria-label', `${item.title}, requiere sesión`); }
      host.append(link);
    }
  };
  section('PLATAFORMA', PUBLIC);
  const own = session ? routes.filter(route => route.roles?.includes(session.user.id_rol)) : [];
  section(session ? 'TU ESPACIO' : 'ÁREAS DE ATENCIÓN', own.length ? own : AREAS, !session);
}

export function setupResponsiveMenu() {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('menu-toggle');
  const closeButton = document.getElementById('menu-close');
  const overlay = document.getElementById('menu-overlay');
  const workspace = document.getElementById('workspace');
  const media = window.matchMedia('(max-width: 800px)');
  toggle.append(icon('menu')); closeButton.append(icon('close'));
  let open = false;
  function setOpen(next, returnFocus = true) {
    const previous = open;
    open = media.matches && next;
    sidebar.classList.toggle('is-open', open);
    sidebar.inert = media.matches && !open;
    workspace.inert = open;
    overlay.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      sidebar.setAttribute('role', 'dialog'); sidebar.setAttribute('aria-modal', 'true');
      closeButton.focus();
    } else {
      sidebar.removeAttribute('role'); sidebar.removeAttribute('aria-modal');
      if (previous && returnFocus && media.matches) toggle.focus();
    }
  }
  toggle.addEventListener('click', () => setOpen(!open));
  closeButton.addEventListener('click', () => setOpen(false));
  overlay.addEventListener('click', () => setOpen(false));
  sidebar.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link) return;
    const wasOpen = open;
    setOpen(false, false);
    if (wasOpen && link.hash === window.location.hash) document.getElementById('main-content').focus();
  });
  document.addEventListener('keydown', event => {
    if (!open) return;
    if (event.key === 'Escape') { event.preventDefault(); setOpen(false); }
    if (event.key === 'Tab') {
      const elements = [...sidebar.querySelectorAll('a[href], button:not([disabled])')];
      const first = elements[0], last = elements.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  media.addEventListener('change', () => setOpen(false, false));
  setOpen(false);
  return { close: () => setOpen(false, false) };
}
