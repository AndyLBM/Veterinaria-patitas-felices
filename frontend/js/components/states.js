import { icon } from './icons.js';
import { button } from './buttons.js';
export function state({ kind = 'empty', title, message, action } = {}) {
  const section = document.createElement('section');
  section.className = `state state-${kind}`;
  if (kind === 'loading') section.setAttribute('role', 'status');
  if (kind === 'error') section.setAttribute('role', 'alert');
  const mark = document.createElement('span');
  mark.className = kind === 'loading' ? 'spinner' : 'state-icon';
  mark.setAttribute('aria-hidden', 'true');
  if (kind !== 'loading') mark.append(icon(kind === 'error' ? 'alert' : 'inbox'));
  const heading = document.createElement('h2');
  heading.textContent = title || ({ loading: 'Cargando…', error: 'No se pudo cargar', empty: 'Todavía no hay contenido' }[kind]);
  const description = document.createElement('p');
  description.textContent = message || '';
  section.append(mark, heading, description);
  if (action) section.append(button(action.label, { onClick: action.onClick, variant: 'secondary' }));
  return section;
}
