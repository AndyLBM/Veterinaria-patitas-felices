export const routes = Object.freeze([
  { path: '/inicio', title: 'Bienvenida', view: 'home.html', page: 'home' },
  { path: '/componentes', title: 'Componentes', view: 'components.html', page: 'components' },
  { path: '/conexion', title: 'Estado de conexión', view: 'connection.html', page: 'connection' },
  { path: '/acceso', title: 'Iniciar sesión', view: 'auth/login.html', page: 'login' },
  { path: '/registro', title: 'Crear cuenta', view: 'auth/register.html', page: 'register' },
  { path: '/acceso-denegado', title: 'Acceso restringido', view: 'shared/notice.html', page: 'denied' },
  { path: '/no-encontrada', title: 'Página no encontrada', view: 'shared/notice.html', page: 'notFound' },
  { path: '/admin/panel', title: 'Panel administrativo', roles: [1], view: 'admin/panel.html', page: 'adminPanel' },
  ...[['cuentas', 'Usuarios'], ['clientes', 'Clientes'], ['veterinarios', 'Veterinarios'], ['especialidades', 'Especialidades'], ['servicios', 'Servicios']].map(([module, title]) => ({ path: `/admin/${module}`, title, roles: [1], view: 'admin/module.html', page: 'adminModule', module })),
  { path: '/admin/horarios', title: 'Horarios', roles: [1], view: 'admin/agenda.html', page: 'adminSchedules' },
  { path: '/admin/citas', title: 'Citas', roles: [1], view: 'admin/agenda.html', page: 'adminAppointments' },
  { path: '/veterinario/panel', title: 'Espacio veterinario', roles: [2], view: 'vet/panel.html', page: 'vetPanel' },
  ...[['agenda','Mi agenda'],['atenciones','Atenciones'],['recetas','Recetas'],['vacunas','Vacunas']].map(([module,title]) => ({ path: `/veterinario/${module}`, title, roles: [2], view: 'vet/workspace.html', page: 'vetWorkspace', module })),
  { path: '/admin/historial', title: 'Historial clínico', roles: [1], view: 'shared/history.html', page: 'history' },
  { path: '/veterinario/historial', title: 'Historial clínico', roles: [2], view: 'shared/history.html', page: 'history' },
  { path: '/cliente/panel', title: 'Mi espacio', roles: [3], view: 'client/panel.html', page: 'clientPanel' },
  { path: '/cliente/mascotas', title: 'Mis mascotas', roles: [3], view: 'client/pets.html', page: 'clientPets' },
  { path: '/cliente/perfil', title: 'Mi perfil', roles: [3], view: 'client/profile.html', page: 'clientProfile' },
  { path: '/cliente/reserva', title: 'Reservar una cita', roles: [3], view: 'client/booking.html', page: 'clientBooking' },
  { path: '/cliente/citas', title: 'Mis citas', roles: [3], view: 'client/appointments.html', page: 'clientAppointments' },
  { path: '/cliente/historial', title: 'Historial de mis mascotas', roles: [3], view: 'shared/history.html', page: 'history' },
]);

export function resolveRoute(hash) {
  let path;
  try { path = decodeURIComponent((hash || '#/inicio').replace(/^#/, '').split('?')[0]); }
  catch { return routes.find(route => route.page === 'notFound'); }
  if (path === '/' || path === '') path = '/inicio';
  return routes.find(route => route.path === path) || routes.find(route => route.page === 'notFound');
}
