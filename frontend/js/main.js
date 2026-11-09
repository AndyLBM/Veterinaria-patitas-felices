import { startRouter } from './core/router.js';
import { renderNavigation, setupResponsiveMenu } from './components/navigation.js';
import { mountNotice } from './pages/notice.js';
import { mountConnection } from './pages/connection.js';
import { mountComponents } from './pages/components.js';
import { ROLE_NAMES } from './config.js';
import { clearSession, onSessionChange, checkSessionExpiration } from './core/session.js';
import { mountAuth } from './pages/auth.js';
import { mountAdminPanel, mountAdminModule } from './pages/admin.js';
import { mountAdminAgenda } from './pages/admin-agenda.js';
import { mountClient } from './pages/client.js';
import { mountClientBooking } from './pages/booking.js';
import { mountClientAppointments } from './pages/client-appointments.js';
import { mountVet } from './pages/vet.js';
import { mountHistory } from './pages/history.js';
import { notify } from './components/feedback.js';

const menu = setupResponsiveMenu();
document.getElementById('logout').addEventListener('click', () => {
  clearSession('logout');
  window.location.hash = '/acceso';
});
document.addEventListener('visibilitychange', () => { if (!document.hidden) checkSessionExpiration(); });
window.addEventListener('focus', checkSessionExpiration);
onSessionChange((session, event) => {
  if (!session) {
    document.getElementById('notifications').replaceChildren();
    if (event?.hadSession && event.reason === 'expired') notify('Tu sesión ha vencido. Inicia sesión nuevamente.');
  }
});
document.querySelector('.skip-link').addEventListener('click', event => {
  event.preventDefault();
  const main = document.getElementById('main-content');
  main.focus(); main.scrollIntoView();
});

startRouter({
  host: document.getElementById('view'),
  onNavigate(route, session) {
    menu.close();
    document.getElementById('route-label').textContent = route.title;
    document.getElementById('session-label').textContent = session ? ROLE_NAMES[session.user.id_rol] : 'Sin sesión';
    document.body.dataset.authenticated = String(Boolean(session));
    document.getElementById('header-access').hidden = Boolean(session);
    document.getElementById('logout').hidden = !session;
    renderNavigation(document.getElementById('main-navigation'), route.path, session);
  },
  mount(page, context) {
    if (page === 'components') return mountComponents(context);
    if (page === 'connection') return mountConnection(context);
    if (page === 'login' || page === 'register') return mountAuth(page, context);
    if (page === 'adminPanel') return mountAdminPanel(context);
    if (page === 'adminModule') return mountAdminModule(context);
    if (page === 'adminSchedules' || page === 'adminAppointments') return mountAdminAgenda(context);
    if (['clientPanel', 'clientPets', 'clientProfile'].includes(page)) return mountClient(context);
    if (page === 'clientBooking') return mountClientBooking(context);
    if (page === 'clientAppointments') return mountClientAppointments(context);
    if (page === 'vetPanel' || page === 'vetWorkspace') return mountVet(context);
    if (page === 'history') return mountHistory(context);
    if (page !== 'home') return mountNotice(page, context);
  },
});
