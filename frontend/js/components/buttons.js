import { icon } from './icons.js';
export function button(label, { variant = 'primary', iconName, onClick, type = 'button' } = {}) {
  const element = document.createElement('button');
  element.type = type;
  element.className = `button button-${variant}`;
  if (iconName) element.append(icon(iconName));
  element.append(document.createTextNode(label));
  if (onClick) element.addEventListener('click', onClick);
  return element;
}
export async function withBusy(element, task) {
  if (element.disabled || element.getAttribute('aria-busy') === 'true') return;
  const restoreFocus = document.activeElement === element;
  element.disabled = true;
  element.setAttribute('aria-busy', 'true');
  try { return await task(); }
  finally {
    element.disabled = false; element.removeAttribute('aria-busy');
    // Deshabilitar el lanzador puede llevar el foco a body antes de abrir el diálogo.
    // Restaurarlo solo si el flujo no enfocó expresamente otro elemento.
    if (restoreFocus && element.isConnected && document.activeElement === document.body) element.focus();
  }
}
