export function canAccess(route, session) {
  if (!route.roles?.length) return true;
  if (session?.expiresAt && session.expiresAt <= Date.now()) return false;
  return Boolean(session?.accessToken && route.roles.includes(session.user?.id_rol));
}
