import { clientAppointmentsApi as api } from '../api/client-appointments.js';
import { filterOwnAppointments } from '../adapters/booking.js';
import { APPOINTMENT_STATES } from '../adapters/agenda.js';
import { formatLocalDateTime } from '../adapters/dates.js';
import { getSession } from '../core/session.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { button, withBusy } from '../components/buttons.js';
import { state } from '../components/states.js';
import { confirmDialog } from '../components/dialog.js';
import { notify } from '../components/feedback.js';
import { errorMessage } from '../core/errors.js';
import { mountBookingForm } from './booking.js';
const el = (tag, text, cls) => { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; };

export function mountClientAppointments({ host, signal }) {
  if (getSession()?.user.id_rol !== 3) return;
  const list = host.querySelector('[data-own-appointments]'), count = host.querySelector('[data-own-count]');
  const filters = host.querySelector('[data-own-filters]'), fields = host.querySelector('[data-own-filter-fields]');
  const detail = host.querySelector('[data-appointment-detail]'), editor = host.querySelector('[data-appointment-editor]');
  for (const spec of [{ name: 'fecha_desde', label: 'Desde', type: 'date' }, { name: 'fecha_hasta', label: 'Hasta', type: 'date' }, { name: 'estado', label: 'Estado', type: 'select', options: [{ value: '', label: 'Todos los estados' }, ...Object.entries(APPOINTMENT_STATES).map(([value, label]) => ({ value, label }))] }]) fields.append(field({ ...spec, id: `own-${spec.name}` }));
  let rows = [], dataReady = false, generation = 0, interaction = 0, child;
  function clear() { interaction++; child?.abort(); child = null; editor.hidden = true; editor.replaceChildren(); detail.hidden = true; detail.replaceChildren(); }
  function render() {
    if (signal.aborted || !dataReady) return;
    const visible = filterOwnAppointments(rows, Object.fromEntries(new FormData(filters)));
    count.textContent = `${visible.length} de ${rows.length} citas`;
    list.replaceChildren();
    if (!visible.length) { list.append(state({ kind: 'empty', title: 'Sin citas para mostrar', message: 'Puedes cambiar los filtros o reservar una cita.' })); return; }
    const grid = el('div', null, 'pet-grid');
    for (const r of visible) {
      const card = el('article', null, 'card own-appointment'); card.dataset.appointmentId = r.id_cita;
      card.append(el('span', APPOINTMENT_STATES[r.estado] || r.estado, 'badge badge-outline'), el('h2', r.nombre_mascota), el('p', r.nombre_servicio), el('p', `${r.nombre_veterinario} ${r.apellido_veterinario}`, 'client-note'), el('p', formatLocalDateTime(r.fecha_inicio)), el('small', 'Hora de Lima'));
      const b = button('Ver detalle', { variant: 'secondary', onClick: () => show(r.id_cita) }); b.dataset.action = 'view-own-appointment'; b.setAttribute('aria-label', `Ver cita ${r.id_cita} de ${r.nombre_mascota}`); card.append(b); grid.append(card);
    } list.append(grid);
  }
  filters.addEventListener('submit', e => {
    e.preventDefault(); if (!validateForm(filters)) return;
    if (filters.elements.fecha_desde.value && filters.elements.fecha_hasta.value && filters.elements.fecha_desde.value > filters.elements.fecha_hasta.value) { setFieldError(filters.elements.fecha_hasta, 'La fecha final debe ser igual o posterior a la inicial.'); filters.elements.fecha_hasta.focus(); return; }
    render();
  }, { signal });
  filters.addEventListener('reset', () => queueMicrotask(render), { signal });
  filters.addEventListener('input', e => setFieldError(e.target), { signal });
  host.querySelector('[data-own-refresh]').addEventListener('click', load, { signal });
  async function load() {
    const version = ++generation; dataReady = false; count.textContent = ''; list.setAttribute('aria-busy', 'true'); list.replaceChildren(state({ kind: 'loading', title: 'Consultando tus citas…' }));
    try { const result = await api.list({ signal }); if (signal.aborted || version !== generation) return; rows = result; dataReady = true; render(); }
    catch (error) { if (!signal.aborted && version === generation) list.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: load } })); }
    finally { if (!signal.aborted && version === generation) list.removeAttribute('aria-busy'); }
  }
  async function show(id) {
    clear(); const version = interaction; detail.hidden = false; detail.append(state({ kind: 'loading', title: 'Consultando cita…' }));
    try {
      const r = await api.get(id, { signal }); if (signal.aborted || version !== interaction) return;
      detail.replaceChildren(); const heading = el('h2', `Cita ${r.id_cita}`); heading.tabIndex = -1; detail.append(heading); heading.focus();
      const dl = el('dl', null, 'client-detail-grid');
      for (const [label, value] of [['Mascota', r.nombre_mascota], ['Servicio', r.nombre_servicio], ['Veterinario', `${r.nombre_veterinario} ${r.apellido_veterinario}`], ['Inicio · Lima', formatLocalDateTime(r.fecha_inicio)], ['Fin · Lima', formatLocalDateTime(r.fecha_fin)], ['Duración original', `${r.duracion_minutos} minutos`], ['Estado', APPOINTMENT_STATES[r.estado] || r.estado], ['Motivo', r.motivo || 'Sin indicar']]) dl.append(el('dt', label), el('dd', value));
      detail.append(dl);
      if (['PROGRAMADA', 'CONFIRMADA'].includes(r.estado)) {
        detail.append(el('p', 'Cancelación y reprogramación hasta 24 horas antes del inicio. El servidor comprobará el plazo y el estado al realizar la operación.', 'client-note'));
        const actions = el('div', null, 'button-row');
        const move = button('Reprogramar fecha y hora', { variant: 'secondary', onClick: () => {
          child?.abort(); child = new AbortController(); editor.hidden = false;
          mountBookingForm({ host: editor, signal: child.signal, appointment: r, onSaved: async () => { if (!signal.aborted) { notify('Cita reprogramada.', { tone: 'success', key: 'client-result' }); await load(); await show(id); } } });
        } }); move.dataset.action = 'reprogram-own';
        const cancel = button('Cancelar cita', { variant: 'secondary', onClick: () => withBusy(cancel, async () => {
          if (!await confirmDialog({ title: 'Cancelar cita', message: `${r.nombre_mascota} · ${r.nombre_servicio} · ${formatLocalDateTime(r.fecha_inicio)} (Lima). El servidor validará si todavía puedes cancelarla.`, confirmLabel: 'Cancelar cita', signal }) || signal.aborted) return;
          try { await api.cancel(id, { signal }); if (signal.aborted) return; notify('Cita cancelada.', { tone: 'success', key: 'client-result' }); await load(); await show(id); }
          catch (error) { if (!signal.aborted) { const alert = state({ kind: 'error', title: 'No se pudo cancelar', message: errorMessage(error) }); detail.querySelector('[data-cancel-error]')?.remove(); alert.dataset.cancelError = ''; detail.append(alert); } }
        }) }); cancel.dataset.action = 'cancel-own'; actions.append(move, cancel); detail.append(actions);
      } else detail.append(el('p', 'Este estado no permite cancelar o reprogramar desde tu espacio.', 'client-note'));
      detail.append(button('Cerrar detalle', { variant: 'secondary', onClick: () => { clear(); host.querySelector('[data-own-refresh]').focus(); } }));
    } catch (error) { if (!signal.aborted && version === interaction) detail.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); }
  }
  signal.addEventListener('abort', clear, { once: true });
  load().then(() => { if (!signal.aborted) { const id = Number(new URLSearchParams(window.location.hash.split('?')[1] || '').get('id_cita')); if (Number.isSafeInteger(id) && id > 0) show(id); } });
}
