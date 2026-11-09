import { button } from '../components/buttons.js';
import { field, validateForm } from '../components/forms.js';
import { table } from '../components/table.js';
import { confirmDialog } from '../components/dialog.js';
import { notify } from '../components/feedback.js';
import { state } from '../components/states.js';

export function mountComponents({ host, signal }) {
  const actions = host.querySelector('[data-demo-buttons]');
  actions.append(button('Acción principal', { iconName: 'check', onClick: () => notify('Demostración de botón. No se enviaron datos.', { tone: 'success' }) }), button('Acción secundaria', { variant: 'secondary', onClick: () => notify('Acción de demostración local.') }));
  const form = host.querySelector('[data-demo-form]');
  form.append(field({ id: 'demo-message', label: 'Texto de demostración', hint: 'Este campo solo prueba la validación local. No se guarda.', required: true }), button('Comprobar campo', { type: 'submit' }));
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (validateForm(form)) notify('Validación correcta. No se enviaron ni guardaron datos.', { tone: 'success' });
  }, { signal });
  host.querySelector('[data-demo-table]').append(table({ caption: 'Estructura de tabla · sin datos conectados', columns: [{ key: 'recurso', label: 'Recurso' }, { key: 'estado', label: 'Estado' }, { key: 'acciones', label: 'Acciones' }], emptyMessage: 'Sin registros. Esta tabla es una muestra de componente.' }));
  const openDialog = host.querySelector('[data-demo-dialog]');
  openDialog.addEventListener('click', async () => {
    if (document.querySelector('dialog[open]')) return;
    const accepted = await confirmDialog({ title: 'Un momento para confirmar', message: 'Este diálogo es una demostración. Ninguna opción modifica datos.', confirmLabel: 'Entendido', signal });
    if (!signal.aborted && accepted) notify('Diálogo confirmado. No se realizó ninguna operación.', { tone: 'success' });
  }, { signal });
  host.querySelector('[data-demo-notify]').addEventListener('click', () => notify('Los avisos se pueden cerrar cuando termines de leerlos.'), { signal });
  const slot = host.querySelector('[data-demo-state]');
  const renderState = kind => slot.replaceChildren(state({ kind, title: { empty: 'Sin contenido todavía', loading: 'Cargando contenido…', error: 'No se pudo cargar el contenido' }[kind], message: 'Ejemplo visual de estado. No corresponde a registros reales.' }));
  for (const control of host.querySelectorAll('[data-state-kind]')) control.addEventListener('click', () => renderState(control.dataset.stateKind), { signal });
  renderState('empty');
}
