export const API_BASE_URL = globalThis.document?.querySelector('meta[name="api-base"]')?.content || '/api/';
export const APP_NAME = 'Patitas Felices';
export const ROLES = Object.freeze({ ADMIN: 1, VETERINARIO: 2, CLIENTE: 3 });
export const ROLE_NAMES = Object.freeze({ 1: 'Administrador', 2: 'Veterinario', 3: 'Cliente' });
