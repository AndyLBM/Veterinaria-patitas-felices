import { agendaApi } from '../api/agenda.js';
import { adminApi } from '../api/admin.js';
import { WEEKDAYS, APPOINTMENT_STATES, TRANSITIONS, groupSchedules, validHours } from '../adapters/agenda.js';
import { formatLocalDateTime } from '../adapters/dates.js';
import { button, withBusy } from '../components/buttons.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { table } from '../components/table.js';
import { state } from '../components/states.js';
import { confirmDialog } from '../components/dialog.js';
import { notify } from '../components/feedback.js';
import { errorMessage } from '../core/errors.js';
import { getSession } from '../core/session.js';

const el = (tag, text, className) => { const n = document.createElement(tag); if (text != null) n.textContent = text; if (className) n.className = className; return n; };
const person = (row, type) => `${row[`nombre_${type}`] || ''} ${row[`apellido_${type}`] || ''}`.trim();
export const appointmentColumns = [
  { key: 'id_cita', label: 'ID' }, { key: 'nombre_mascota', label: 'Mascota' },
  { key: 'nombre_cliente', label: 'Cliente', format: (_, r) => person(r, 'cliente') },
  { key: 'nombre_servicio', label: 'Servicio' }, { key: 'nombre_veterinario', label: 'Veterinario', format: (_, r) => person(r, 'veterinario') },
  { key: 'fecha_inicio', label: 'Inicio · Lima', format: formatLocalDateTime },
  { key: 'fecha_fin', label: 'Fin · Lima', format: formatLocalDateTime },
  { key: 'estado', label: 'Estado', format: v => APPOINTMENT_STATES[v] || v },
];

export function mountAdminAgenda({ host, signal, route }) {
  if (getSession()?.user.id_rol !== 1) return;
  const schedules = route.page === 'adminSchedules';
  const title = schedules ? 'Horarios de veterinarios' : 'Supervisión de citas';
  host.querySelector('[data-agenda-title]').textContent = title;
  host.querySelector('[data-agenda-description]').textContent = schedules ? 'Horarios semanales por veterinario y día. Lunes = 1; domingo = 7. No hay activación ni desactivación de horarios.' : 'Consulta las citas y sus estados. Fechas y horas de Lima. Los cambios se validan en el servidor.';
  const filters = host.querySelector('[data-agenda-filters]'), fields = host.querySelector('[data-agenda-fields]');
  const slot = host.querySelector('[data-agenda-list]'), count = host.querySelector('[data-agenda-count]');
  const editor = host.querySelector('[data-agenda-editor]'), detail = host.querySelector('[data-agenda-detail]');
  const tools = host.querySelector('[data-agenda-tools]');
  let rows = [], vets = [], generation = 0, interaction = 0, writing = false, request;
  const options = { signal };
  function control(form, container, spec) { const wrap = field({ ...spec, id: `${form === filters ? 'agenda-filter' : 'agenda'}-${spec.name}` }); container.append(wrap); return form.elements[spec.name]; }
  const vetFilter = control(filters, fields, { name: 'id_veterinario', label: 'Veterinario', type: 'select', options: [{ value: '', label: 'Todos los veterinarios' }] });
  if (!schedules) {
    control(filters, fields, { name: 'id_cliente', label: 'Cliente', type: 'select', options: [{ value: '', label: 'Todos los clientes' }] });
    control(filters, fields, { name: 'fecha_desde', label: 'Desde', type: 'date' });
    control(filters, fields, { name: 'fecha_hasta', label: 'Hasta', type: 'date' });
    control(filters, fields, { name: 'estado', label: 'Estado', type: 'select', options: [{ value: '', label: 'Todos los estados' }, ...Object.entries(APPOINTMENT_STATES).map(([value, label]) => ({ value, label }))] });
  }
  const apply = button('Aplicar filtros', { type: 'submit' }); apply.dataset.action = 'filter';
  const reset = button('Limpiar filtros', { variant: 'secondary', onClick: () => { if (!writing) { filters.reset(); load(); } } });
  host.querySelector('[data-agenda-filter-actions]').append(apply, reset);
  const refresh = button('Actualizar', { variant: 'secondary', onClick: () => { if (!writing) load(); } }); tools.append(refresh);
  const create = schedules ? button('Registrar horario', { onClick: () => { if (!writing) editSchedule(); } }) : null;
  if (create) { create.dataset.action = 'create-schedule'; tools.append(create); }
  filters.addEventListener('submit', event => {
    event.preventDefault(); if (writing || !validateForm(filters)) return;
    if (!schedules && filters.elements.fecha_desde.value && filters.elements.fecha_hasta.value && filters.elements.fecha_desde.value > filters.elements.fecha_hasta.value) { setFieldError(filters.elements.fecha_hasta, 'La fecha final debe ser igual o posterior a la inicial.'); filters.elements.fecha_hasta.focus(); return; }
    load();
  }, options);
  filters.addEventListener('input', e => { if (e.target.matches('input,select')) setFieldError(e.target); }, options);
  function closePanels() { interaction++; editor.hidden = true; editor.replaceChildren(); detail.hidden = true; detail.replaceChildren(); }
  function heading(panel, text) { const h = el('h2', text); h.tabIndex = -1; panel.append(h); h.focus(); }
  function addChoices(select, records, key, label) {
    for (const row of records) if (![...select.options].some(o => o.value === String(row[key]))) { const o = document.createElement('option'); o.value = row[key]; o.textContent = label(row); select.append(o); }
  }
  async function load() {
    const current = ++generation; request?.abort(); request = new AbortController();
    const query = Object.fromEntries(new FormData(filters));
    apply.disabled = true; slot.setAttribute('aria-busy', 'true'); count.textContent = '';
    slot.replaceChildren(state({ kind: 'loading', title: 'Consultando información…' }));
    try {
      if (schedules) {
        const [result, catalog] = await Promise.all([agendaApi.schedules(query.id_veterinario, { signal: request.signal }), adminApi.list('veterinarios', { signal: request.signal })]);
        if (signal.aborted || current !== generation) return;
        rows = result; vets = catalog;
        addChoices(vetFilter, vets, 'id_veterinario', v => `${v.nombre} ${v.apellido}${v.estado !== 'ACTIVO' ? ' · Inactivo' : ''}`);
      } else {
        const result = await agendaApi.appointments(query, { signal: request.signal });
        if (signal.aborted || current !== generation) return;
        rows = result;
        addChoices(vetFilter, rows, 'id_veterinario', r => person(r, 'veterinario'));
        addChoices(filters.elements.id_cliente, rows, 'id_cliente', r => person(r, 'cliente'));
      }
      render();
    } catch (error) { if (!signal.aborted && current === generation) slot.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: load } })); }
    finally { if (!signal.aborted && current === generation) { apply.disabled = false; slot.removeAttribute('aria-busy'); } }
  }
  function render() {
    count.textContent = `${rows.length} registros encontrados`;
    slot.replaceChildren();
    if (!rows.length) { slot.append(state({ kind: 'empty', title: 'Sin resultados', message: 'No hay registros para los filtros seleccionados.' })); return; }
    if (!schedules) {
      slot.append(table({ caption: 'Citas', rowKey: 'id_cita', rows, columns: [...appointmentColumns, { label: 'Acciones', render: row => { const b = button('Ver cita', { variant: 'secondary', onClick: () => { if (!writing) showAppointment(row.id_cita); } }); b.dataset.action = 'view-appointment'; b.setAttribute('aria-label', `Ver cita ${row.id_cita} de ${row.nombre_mascota}`); return b; } }] })); return;
    }
    for (const group of groupSchedules(rows)) {
      const first = group[0], section = el('section', null, 'schedule-group');
      const name = person(first, 'veterinario');
      section.append(el('h2', `${name}${first.estado_veterinario !== 'ACTIVO' ? ' · Inactivo' : ''}`));
      section.append(table({ caption: `Horario semanal de ${name}`, rowKey: 'id_horario', rows: group, columns: [
        { key: 'id_horario', label: 'ID' }, { key: 'dia_semana', label: 'Día', format: d => WEEKDAYS[d - 1] || 'Día no disponible' }, { key: 'hora_inicio', label: 'Desde' }, { key: 'hora_fin', label: 'Hasta' },
        { label: 'Acciones', render: row => { const b = button('Editar horario', { variant: 'secondary', onClick: () => { if (!writing) editSchedule(row.id_horario); } }); b.dataset.action = 'edit-schedule'; b.setAttribute('aria-label', `Editar horario ${row.id_horario}, ${WEEKDAYS[row.dia_semana - 1]}`); return b; } },
      ] })); slot.append(section);
    }
  }
  async function editSchedule(id) {
    closePanels(); const version = interaction; editor.hidden = false;
    editor.append(state({ kind: 'loading', title: 'Preparando horario…' }));
    try {
      const [record, catalog] = await Promise.all([id ? agendaApi.schedule(id, options) : null, adminApi.list('veterinarios', options)]);
      if (signal.aborted || version !== interaction) return;
      const eligible = catalog.filter(v => v.estado === 'ACTIVO' || v.id_veterinario === record?.id_veterinario);
      editor.replaceChildren(); heading(editor, record ? 'Editar horario' : 'Registrar horario');
      if (!eligible.length) { editor.append(state({ kind: 'empty', title: 'Sin veterinarios activos', message: 'Registra o activa un veterinario antes de asignarle un horario.' })); return; }
      const form = el('form'); form.noValidate = true; form.dataset.scheduleForm = '';
      const grid = el('div', null, 'admin-form-grid'); form.append(grid);
      const vet = control(form, grid, { name: 'id_veterinario', label: 'Veterinario', type: 'select', required: true, options: [{ value: '', label: 'Selecciona un veterinario' }, ...eligible.map(v => ({ value: String(v.id_veterinario), label: `${v.nombre} ${v.apellido}` }))] });
      const day = control(form, grid, { name: 'dia_semana', label: 'Día de la semana', type: 'select', required: true, options: [{ value: '', label: 'Selecciona un día' }, ...WEEKDAYS.map((label, i) => ({ value: String(i + 1), label: `${label} (${i + 1})` }))] });
      const start = control(form, grid, { name: 'hora_inicio', label: 'Hora de inicio', type: 'time', required: true, step: 1 });
      const end = control(form, grid, { name: 'hora_fin', label: 'Hora de fin', type: 'time', required: true, step: 1 });
      if (record) { vet.value = record.id_veterinario; vet.disabled = true; day.value = record.dia_semana; start.value = record.hora_inicio; end.value = record.hora_fin; }
      const alert = el('div', null, 'auth-error'); alert.hidden = true; alert.setAttribute('role', 'alert'); alert.tabIndex = -1; form.prepend(alert);
      const actions = el('div', null, 'button-row'); const save = button('Guardar horario', { type: 'submit' }); save.dataset.action = 'save-schedule';
      const cancel = button('Cancelar', { variant: 'secondary', onClick: () => { if (!writing) { closePanels(); create.focus(); } } }); actions.append(save, cancel); form.append(actions); editor.append(form);
      if (record && eligible.find(v => v.id_veterinario === record.id_veterinario)?.estado !== 'ACTIVO') { save.disabled = true; editor.append(el('p', 'El veterinario está inactivo. El servidor no permite modificar sus horarios.', 'admin-footnote')); }
      form.addEventListener('input', event => setFieldError(event.target), options);
      form.addEventListener('submit', async event => {
        event.preventDefault(); if (writing || save.disabled || !validateForm(form)) return;
        if (!validHours(start.value, end.value)) { setFieldError(end, 'La hora de fin debe ser posterior al inicio, dentro del mismo día.'); end.focus(); return; }
        await withBusy(save, async () => {
          if (record && !await confirmDialog({ title: 'Modificar horario', message: 'Se actualizará el horario semanal. Las citas ya registradas conservan sus datos.', confirmLabel: 'Guardar cambios', signal })) return;
          if (signal.aborted) return;
          writing = true; cancel.disabled = true;
          try {
            const values = Object.fromEntries(new FormData(form));
            if (record) await agendaApi.updateSchedule(record.id_horario, values, options); else await agendaApi.createSchedule(values, options);
            if (signal.aborted) return;
            closePanels(); notify('Horario guardado correctamente.', { tone: 'success', key: 'admin-result' }); await load(); create.focus();
          } catch (error) {
            if (signal.aborted) return;
            alert.hidden = false; alert.textContent = errorMessage(error); alert.focus();
            for (const f of error.fields || []) if (form.elements[f.field]) setFieldError(form.elements[f.field], f.message);
          } finally { writing = false; cancel.disabled = false; }
        });
      }, options);
    } catch (error) { if (!signal.aborted && version === interaction) editor.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); }
  }
  async function showAppointment(id) {
    closePanels(); const version = interaction; detail.hidden = false; detail.append(state({ kind: 'loading', title: 'Consultando cita…' }));
    try {
      const fresh = await agendaApi.appointment(id, options);
      if (signal.aborted || version !== interaction) return;
      detail.replaceChildren(); heading(detail, `Cita ${fresh.id_cita}`);
      const dl = el('dl', null, 'admin-detail-grid');
      for (const c of [...appointmentColumns.slice(1), { key: 'duracion_minutos', label: 'Duración (minutos)' }, { key: 'motivo', label: 'Motivo' }]) dl.append(el('dt', c.label), el('dd', c.format ? c.format(fresh[c.key], fresh) : fresh[c.key] ?? 'Sin indicar'));
      detail.append(dl);
      const allowed = TRANSITIONS[fresh.estado] || [];
      if (allowed.length) {
        const form = el('form'); form.noValidate = true; form.dataset.appointmentStateForm = '';
        const select = control(form, form, { name: 'estado_nuevo', label: 'Cambiar estado', type: 'select', required: true, options: [{ value: '', label: 'Selecciona el nuevo estado' }, ...allowed.map(value => ({ value, label: APPOINTMENT_STATES[value] }))] });
        if (fresh.estado === 'EN_ATENCION') form.append(el('p', 'Finalizar exige atención, triaje y consulta completos. El servidor comprobará estos requisitos.', 'admin-footnote'));
        const alert = el('div', null, 'auth-error'); alert.hidden = true; alert.setAttribute('role', 'alert'); alert.tabIndex = -1; form.append(alert);
        const save = button('Actualizar estado', { type: 'submit' }); save.dataset.action = 'save-appointment-state'; form.append(save); detail.append(form);
        form.addEventListener('submit', async event => {
          event.preventDefault(); if (writing || !validateForm(form)) return;
          await withBusy(save, async () => {
            if (!await confirmDialog({ title: 'Cambiar estado de la cita', message: `Cita ${fresh.id_cita}: de ${APPOINTMENT_STATES[fresh.estado]} a ${APPOINTMENT_STATES[select.value]}.`, confirmLabel: 'Confirmar cambio', signal }) || signal.aborted) return;
            writing = true;
            try {
              await agendaApi.changeState(fresh.id_cita, select.value, options);
              if (signal.aborted) return;
              notify('Estado de la cita actualizado.', { tone: 'success', key: 'admin-result' }); await load(); await showAppointment(fresh.id_cita);
            } catch (error) { if (!signal.aborted) { alert.textContent = errorMessage(error); alert.hidden = false; alert.focus(); } }
            finally { writing = false; }
          });
        }, options);
      } else detail.append(el('p', 'Este estado no admite más transiciones.', 'admin-footnote'));
      detail.append(button('Cerrar detalle', { variant: 'secondary', onClick: () => { if (!writing) { closePanels(); apply.focus(); } } }));
    } catch (error) { if (!signal.aborted && version === interaction) detail.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); }
  }
  signal.addEventListener('abort', () => { request?.abort(); closePanels(); }, { once: true });
  load().then(() => {
    if (!schedules && !signal.aborted) { const value = new URLSearchParams(window.location.hash.split('?')[1] || '').get('id_cita'); if (value && Number.isSafeInteger(Number(value)) && Number(value) > 0) showAppointment(Number(value)); }
  });
}
