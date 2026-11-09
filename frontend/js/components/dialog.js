import { button } from './buttons.js';
let sequence = 0;
export function confirmDialog({ title, message, confirmLabel = 'Entendido', signal }) {
  if (signal?.aborted) return Promise.resolve(false);
  return new Promise(resolve => {
    const previousFocus = document.activeElement;
    const dialog = document.createElement('dialog');
    const id = `dialog-${++sequence}`;
    dialog.setAttribute('aria-labelledby', `${id}-title`);
    dialog.setAttribute('aria-describedby', `${id}-message`);
    const heading = document.createElement('h2'); heading.id = `${id}-title`; heading.textContent = title;
    const text = document.createElement('p'); text.id = `${id}-message`; text.textContent = message;
    const actions = document.createElement('div'); actions.className = 'button-row';
    let confirmed = false;
    const cancel = button('Cerrar', { variant: 'secondary', onClick: () => dialog.close() });
    const confirm = button(confirmLabel, { onClick: () => { confirmed = true; dialog.close(); } });
    actions.append(cancel, confirm); dialog.append(heading, text, actions);
    dialog.addEventListener('keydown', event => {
      if (event.key !== 'Tab') return;
      if (event.shiftKey && document.activeElement === cancel) { event.preventDefault(); confirm.focus(); }
      else if (!event.shiftKey && document.activeElement === confirm) { event.preventDefault(); cancel.focus(); }
    });
    const abort = () => dialog.close();
    signal?.addEventListener('abort', abort, { once: true });
    dialog.addEventListener('close', () => {
      signal?.removeEventListener('abort', abort);
      dialog.remove();
      if (previousFocus?.isConnected) previousFocus.focus();
      resolve(confirmed);
    }, { once: true });
    // El diálogo nativo aporta fondo inerte, Escape y gestión de foco modal.
    document.body.append(dialog); dialog.showModal(); cancel.focus();
  });
}
