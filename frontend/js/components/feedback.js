import { icon } from './icons.js';
export function notify(message, { tone = 'info', key } = {}) {
  const host = document.getElementById('notifications');
  if (!host) return;
  // Sin desaparición automática: se permite leer y cerrar a cualquier ritmo.
  const element = document.createElement('div');
  // Un canal opcional conserva el resultado más reciente sin acumular avisos.
  if (key) {
    for (const previous of [...host.children]) if (previous.dataset.notificationKey === key) previous.remove();
    element.dataset.notificationKey = key;
  }
  element.className = 'notification';
  element.dataset.tone = tone;
  const text = document.createElement('p');
  text.textContent = message;
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'icon-button';
  close.setAttribute('aria-label', 'Cerrar notificación');
  close.append(icon('close'));
  close.addEventListener('click', () => element.remove());
  element.append(icon(tone === 'success' ? 'check' : tone === 'error' ? 'alert' : 'info'), text, close);
  host.append(element);
}
