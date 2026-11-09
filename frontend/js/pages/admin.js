import { adminApi } from '../api/admin.js';
import { ADMIN_MODULES, adminFields, matchingRecords } from '../adapters/admin.js';
import { button, withBusy } from '../components/buttons.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { table } from '../components/table.js';
import { state } from '../components/states.js';
import { confirmDialog } from '../components/dialog.js';
import { notify } from '../components/feedback.js';
import { icon } from '../components/icons.js';
import { errorMessage } from '../core/errors.js';
import { getSession, clearSession } from '../core/session.js';
import { agendaApi } from '../api/agenda.js';
import { dashboardSummary, upcomingAppointments, limaNow, APPOINTMENT_STATES } from '../adapters/agenda.js';
import { formatLocalDateTime } from '../adapters/dates.js';

function node(tag, text, className) { const el = document.createElement(tag); if (text != null) el.textContent = text; if (className) el.className = className; return el; }
function statusBadge(value) { const el = node('span', value === 'ACTIVO' ? 'Activo' : 'Inactivo', 'admin-status'); el.dataset.state = value; return el; }

export function mountAdminPanel({ host, signal }) {
  if (getSession()?.user.id_rol !== 1) return;
  const cards = host.querySelector('[data-admin-cards]');
  const loaders = [];
  for (const [key, module] of Object.entries(ADMIN_MODULES)) {
    const card = node('article', null, 'card admin-module-card');
    card.dataset.adminCard = key;
    const top = node('div', null, 'admin-card-top');
    const tile = node('span', null, 'icon-tile'); tile.append(icon(key === 'servicios' ? 'heart' : key === 'especialidades' ? 'book' : 'users'));
    const count = node('span', 'Consultando…', 'admin-card-count'); count.setAttribute('role', 'status');
    top.append(tile, count);
    const link = node('a', `Abrir ${module.title.toLowerCase()} →`); link.href = `#/admin/${key}`;
    card.append(top, node('h2', module.title), node('p', module.note), link); cards.append(card);
    let sequence = 0;
    const load = () => {
      const version = ++sequence; count.textContent = 'Consultando…';
      return adminApi.list(key, { signal }).then(rows => { if (!signal.aborted && version === sequence) count.textContent = dashboardSummary(key, rows); }).catch(error => { if (!signal.aborted && version === sequence) count.textContent = error.status === 403 ? 'Acceso denegado' : 'Total no disponible'; });
    };
    loaders.push(load); load();
  }
  const upcoming = host.querySelector('[data-upcoming]');
  let sequence = 0;
  async function loadUpcoming() {
    const version = ++sequence, now = limaNow();
    upcoming.replaceChildren(state({ kind: 'loading', title: 'Consultando próximas citas…' }));
    try {
      const rows = upcomingAppointments(await agendaApi.appointments({ fecha_desde: now.slice(0, 10) }, { signal }), now);
      if (signal.aborted || version !== sequence) return;
      if (!rows.length) { upcoming.replaceChildren(state({ kind: 'empty', title: 'Sin próximas citas', message: 'No hay citas futuras programadas o confirmadas en la información consultada.' })); return; }
      upcoming.replaceChildren(table({ caption: 'Próximas citas · hora de Lima', rowKey: 'id_cita', rows, columns: [
        { key: 'nombre_mascota', label: 'Mascota' }, { key: 'nombre_servicio', label: 'Servicio' },
        { key: 'nombre_veterinario', label: 'Veterinario', format: (_, r) => `${r.nombre_veterinario} ${r.apellido_veterinario}` },
        { key: 'fecha_inicio', label: 'Fecha y hora', format: formatLocalDateTime },
        { key: 'estado', label: 'Estado', format: v => APPOINTMENT_STATES[v] || v },
        { label: 'Detalle', render: row => { const link = node('a', 'Ver cita', 'button button-secondary'); link.href = `#/admin/citas?id_cita=${row.id_cita}`; link.setAttribute('aria-label', `Ver cita ${row.id_cita}`); return link; } },
      ] }));
    } catch (error) { if (!signal.aborted && version === sequence) upcoming.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: loadUpcoming } })); }
  }
  loaders.push(loadUpcoming); loadUpcoming();
  host.querySelector('[data-refresh-panel]').addEventListener('click', event => withBusy(event.currentTarget, () => Promise.all(loaders.map(load => load()))), { signal });
}

export function mountAdminModule({ host, signal, route }) {
  if (getSession()?.user.id_rol !== 1) return;
  const key = route.module, m = ADMIN_MODULES[key];
  if (!m) return;
  host.querySelector('[data-admin-title]').textContent = m.title;
  host.querySelector('[data-admin-description]').textContent = m.note;
  const tools = host.querySelector('[data-admin-tools]');
  const slot = host.querySelector('[data-admin-list]');
  const editor = host.querySelector('[data-admin-editor]');
  const detail = host.querySelector('[data-admin-detail]');
  const count = host.querySelector('[data-admin-count]');
  const filters = host.querySelector('[data-admin-filters]');
  let rows = [], currentLoad = 0, interaction = 0, writing = false, dataReady = false;
  const searchField = field({ id: 'admin-search', label: 'Buscar en el listado', type: 'search', hint: 'Por nombre, correo, identificador u otros datos visibles.' });
  const search = searchField.querySelector('input'); filters.append(searchField);
  let stateFilter;
  if (m.state && key !== 'clientes') {
    const f = field({ id: 'admin-state-filter', label: 'Estado', type: 'select', options: [{ value: '', label: 'Todos los estados' }, { value: 'ACTIVO', label: 'Activos' }, { value: 'INACTIVO', label: 'Inactivos' }] });
    stateFilter = f.querySelector('select'); filters.append(f); stateFilter.addEventListener('change', render, { signal });
  }
  search.addEventListener('input', render, { signal });
  const refresh = button('Actualizar', { variant: 'secondary', onClick: () => { if (!writing) load(); } }); refresh.dataset.action = 'refresh'; tools.append(refresh);
  const create = m.create ? button(`Registrar ${m.singular}`, { onClick: () => openEditor() }) : null;
  if (create) { create.dataset.action = 'create'; tools.append(create); }

  function closePanels() { interaction++; editor.replaceChildren(); editor.hidden = true; detail.replaceChildren(); detail.hidden = true; }
  function focusTitle(panel) { const h = panel.querySelector('h2'); h.tabIndex = -1; h.focus(); }
  function render() {
    if (signal.aborted || !dataReady) return;
    const visible = matchingRecords(rows, search.value, stateFilter?.value);
    count.textContent = `${visible.length} de ${rows.length} registros`;
    slot.replaceChildren(table({ caption: m.title, rowKey: m.pk, rows: visible, emptyMessage: rows.length ? 'No hay resultados para estos filtros.' : 'Todavía no hay registros.', columns: [
      { key: m.pk, label: 'ID' }, ...m.columns,
      ...(m.state ? [{ key: 'estado', label: 'Estado', render: row => statusBadge(row.estado) }] : []),
      { label: 'Acciones', render: row => {
        const actions = node('div', null, 'admin-row-actions');
        const add = (label, action, fn) => { const b = button(label, { variant: 'secondary', onClick: () => { if (!writing) fn(b); } }); b.dataset.action = action; b.setAttribute('aria-label', `${label}: ${row.nombre} ${row.apellido || ''}`.trim()); actions.append(b); };
        add('Ver', 'view', () => openRecord(row, false));
        if (m.edit) add('Editar', 'edit', () => openRecord(row, true));
        if (m.state) add(row.estado === 'ACTIVO' ? 'Desactivar' : 'Activar', 'state', b => changeState(row, b));
        return actions;
      } },
    ] }));
  }
  async function load() {
    const version = ++currentLoad;
    dataReady = false;
    refresh.disabled = true; count.textContent = '';
    slot.setAttribute('aria-busy', 'true'); slot.replaceChildren(state({ kind: 'loading', title: 'Consultando registros…' }));
    try {
      const result = await adminApi.list(key, { signal });
      if (signal.aborted || version !== currentLoad) return;
      rows = result; dataReady = true; render();
    } catch (error) {
      if (signal.aborted || version !== currentLoad) return;
      rows = []; slot.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: load } }));
    } finally { if (!signal.aborted && version === currentLoad) { refresh.disabled = false; slot.removeAttribute('aria-busy'); } }
  }
  async function openRecord(row, edit) {
    closePanels(); const version = interaction;
    detail.hidden = false; detail.replaceChildren(state({ kind: 'loading', title: 'Consultando información…' }));
    try {
      const fresh = await adminApi.get(key, row[m.pk], { signal });
      if (signal.aborted || interaction !== version) return;
      if (edit) { await openEditor(fresh); return; }
      detail.replaceChildren(node('h2', `Información de ${m.singular}`));
      const dl = node('dl', null, 'admin-detail-grid');
      const columns = [{ key: m.pk, label: 'Identificador' }, ...m.columns,
        ...['apellido', 'telefono', 'fecha_registro', 'id_usuario', 'id_cliente', 'id_veterinario', 'numero_colegiatura', 'id_especialidad', 'descripcion', 'estado'].filter(k => !m.columns.some(c => c.key === k) && k !== m.pk).map(k => ({ key: k, label: { apellido: 'Apellido', telefono: 'Teléfono', fecha_registro: 'Fecha de registro', id_usuario: 'ID de usuario', id_cliente: 'ID de cliente', id_veterinario: 'ID de veterinario', numero_colegiatura: 'Colegiatura', id_especialidad: 'ID de especialidad', descripcion: 'Descripción', estado: 'Estado' }[k] }))];
      for (const c of columns) if (c.key in fresh) dl.append(node('dt', c.label), node('dd', c.format ? c.format(fresh[c.key], fresh) : fresh[c.key] ?? 'Sin definir'));
      detail.append(dl, button('Cerrar información', { variant: 'secondary', onClick: () => { closePanels(); search.focus(); } })); focusTitle(detail);
    } catch (error) { if (!signal.aborted && interaction === version) detail.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); }
  }
  async function openEditor(record) {
    if (writing) return;
    closePanels(); const version = interaction;
    editor.hidden = false; editor.replaceChildren(state({ kind: 'loading', title: 'Preparando formulario…' }));
    let specialties = [];
    try {
      if (key === 'veterinarios') specialties = await adminApi.list('especialidades', { signal });
      if (signal.aborted || version !== interaction) return;
    } catch (error) { if (!signal.aborted && version === interaction) editor.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); return; }
    if (key === 'veterinarios' && !specialties.length) {
      editor.replaceChildren(state({ kind: 'empty', title: 'Primero registra una especialidad', message: 'Cada veterinario debe estar asociado a una especialidad existente.' })); return;
    }
    editor.replaceChildren(node('h2', `${record ? 'Editar' : 'Registrar'} ${m.singular}`));
    const errorSlot = node('div', null, 'auth-error'); errorSlot.hidden = true; errorSlot.setAttribute('role', 'alert'); errorSlot.tabIndex = -1;
    const form = node('form'); form.noValidate = true; form.dataset.adminForm = key;
    const fields = node('div', null, 'admin-form-grid');
    for (const f of adminFields(key, !record)) {
      const options = f.name === 'id_especialidad' ? [{ value: '', label: 'Selecciona una especialidad' }, ...specialties.map(s => ({ value: String(s.id_especialidad), label: s.nombre }))] : undefined;
      const group = field({ ...f, id: `admin-${f.name}`, options });
      const input = group.querySelector('input,select,textarea'); input.value = record?.[f.name] ?? '';
      fields.append(group);
    }
    const actions = node('div', null, 'button-row');
    const save = button('Guardar', { type: 'submit' }); save.dataset.action = 'save';
    const cancel = button('Cancelar', { variant: 'secondary', onClick: () => { if (!writing) { closePanels(); (create || search).focus(); } } });
    actions.append(save, cancel); form.append(fields, actions); editor.append(errorSlot, form); focusTitle(editor);
    form.addEventListener('input', event => { if (event.target.matches('input,select,textarea')) setFieldError(event.target); }, { signal });
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (writing || signal.aborted) return;
      for (const input of form.querySelectorAll('input,select,textarea')) if (input.type !== 'password') input.value = input.value.trim();
      if (!validateForm(form)) return;
      await withBusy(save, async () => {
        if (record && !await confirmDialog({ title: 'Guardar cambios', message: `Se actualizará la información de ${record.nombre}.`, confirmLabel: 'Guardar cambios', signal })) return;
        if (signal.aborted) return;
        writing = true; cancel.disabled = true;
        const values = Object.fromEntries(new FormData(form));
        try {
          if (record) await adminApi.update(key, record[m.pk], values, { signal });
          else await adminApi.create(key, values, { signal });
          if (signal.aborted) return;
          closePanels(); notify('Información guardada correctamente.', { tone: 'success', key: 'admin-result' }); await load(); (create || search).focus();
        } catch (error) {
          if (signal.aborted) return;
          errorSlot.textContent = errorMessage(error); errorSlot.hidden = false;
          for (const f of error.fields || []) if (form.elements[f.field]) setFieldError(form.elements[f.field], f.message);
          errorSlot.focus();
        } finally { values.password = ''; if (form.elements.password) form.elements.password.value = ''; writing = false; cancel.disabled = false; }
      });
    }, { signal });
  }
  async function changeState(row, control) {
    if (writing || document.querySelector('dialog[open]')) return;
    await withBusy(control, async () => {
      const next = row.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
      const own = row.id_usuario === getSession()?.user.id_usuario;
      const accepted = await confirmDialog({ title: next === 'INACTIVO' ? 'Desactivar acceso' : 'Activar acceso', message: `${row.nombre}: el estado cambiará a ${next === 'ACTIVO' ? 'activo' : 'inactivo'}.${own && next === 'INACTIVO' ? ' Esta es tu cuenta: se cerrará tu sesión.' : ''}`, confirmLabel: 'Confirmar cambio', signal });
      if (!accepted || signal.aborted) return;
      writing = true;
      try {
        await adminApi.setState(key, row, next, { signal });
        if (signal.aborted) return;
        if (own && next === 'INACTIVO') { clearSession('expired'); window.location.hash = '/acceso'; return; }
        closePanels(); notify('Estado actualizado correctamente.', { tone: 'success', key: 'admin-result' }); await load(); search.focus();
      } catch (error) { if (!signal.aborted) notify(errorMessage(error), { tone: 'error', key: 'admin-result' }); }
      finally { writing = false; }
    });
  }
  signal.addEventListener('abort', () => { editor.querySelector('form')?.reset(); closePanels(); }, { once: true });
  load();
}
