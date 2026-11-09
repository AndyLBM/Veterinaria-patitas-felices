import { http } from '../core/http.js';
export function checkApi({ signal } = {}) {
  return http.get('', { auth: false, signal });
}
