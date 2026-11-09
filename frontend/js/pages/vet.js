import { clinicalApi as api } from '../api/clinical.js';
import { CLINICAL_FIELDS, CLINICAL_TITLES, agendaCounts } from '../adapters/clinical.js';
import { APPOINTMENT_STATES } from '../adapters/agenda.js';
import { formatLocalDateTime } from '../adapters/dates.js';
import { petDate } from '../adapters/pets.js';
import { getSession } from '../core/session.js';
import { button, withBusy } from '../components/buttons.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { state } from '../components/states.js';
import { confirmDialog } from '../components/dialog.js';
import { notify } from '../components/feedback.js';
import { errorMessage } from '../core/errors.js';

const el = (tag, text, cls) => { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; };
function values(host, pairs) { const dl = el('dl', null, 'client-detail-grid'); for (const [key, value] of pairs) dl.append(el('dt', key), el('dd', value == null || value === '' ? 'Sin registrar' : value)); host.append(dl); }
function clinicalValues(host, kind, record) { values(host, CLINICAL_FIELDS[kind].map(f => [f.label, f.type === 'date' ? petDate(record[f.name]) : record[f.name]])); }
async function optional(task) { try { return await task; } catch (error) { if (error.status === 404) return null; throw error; } }

export function mountVet({ host, signal, route }) {
  if (getSession()?.user.id_rol !== 2) return;
  if (route.page === 'vetPanel') {
    const profile = getSession().profile;
    host.querySelector('[data-vet-welcome]').textContent = profile?.nombre ? `Hola, ${profile.nombre}` : 'Tu espacio veterinario';
    const slot = host.querySelector('[data-vet-dashboard]');
    async function load() {
      slot.replaceChildren(state({ kind: 'loading', title: 'Consultando tu agenda…' }));
      try { const rows = await api.agenda({}, { signal }); if (signal.aborted) return;
        const counts = agendaCounts(rows), grid = el('div', null, 'vet-stats');
        for (const [key, label] of [['pendientes', 'Por atender · programadas o confirmadas'], ['enAtencion', 'En atención'], ['atendidas', 'Atendidas']]) { const card = el('article', null, 'card'); card.dataset.vetMetric = key; card.append(el('p', label), el('strong', counts[key])); grid.append(card); } slot.replaceChildren(grid);
      } catch (error) { if (!signal.aborted) slot.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: load } })); }
    } load(); return;
  }
  const titles = { agenda: 'Mi agenda', atenciones: 'Atenciones clínicas', recetas: 'Recetas de mis pacientes', vacunas: 'Vacunas de mis pacientes' };
  host.querySelector('[data-vet-title]').textContent = titles[route.module] || 'Mi agenda';
  const filters = host.querySelector('[data-vet-filters]'), fields = host.querySelector('[data-vet-filter-fields]');
  const agenda = host.querySelector('[data-vet-agenda]'), caseHost = host.querySelector('[data-vet-case]'), editor = host.querySelector('[data-clinical-editor]');
  for (const spec of [{ name: 'fecha_desde', label: 'Desde', type: 'date' }, { name: 'fecha_hasta', label: 'Hasta', type: 'date' }, { name: 'estado', label: 'Estado', type: 'select', options: [{ value: '', label: 'Todos los estados' }, ...Object.entries(APPOINTMENT_STATES).map(([value, label]) => ({ value, label }))] }]) fields.append(field({ ...spec, id: `vet-filter-${spec.name}` }));
  let listVersion = 0, caseVersion = 0, selected, editorController, writing = false;
  function closeEditor() { editorController?.abort(); editorController = null; editor.querySelector('form')?.reset(); editor.replaceChildren(); editor.hidden = true; }
  async function loadAgenda() {
    const version = ++listVersion; agenda.setAttribute('aria-busy', 'true'); agenda.replaceChildren(state({ kind: 'loading', title: 'Consultando citas asignadas…' }));
    try {
      const rows = await api.agenda(Object.fromEntries(new FormData(filters)), { signal }); if (signal.aborted || version !== listVersion) return;
      agenda.replaceChildren(); if (!rows.length) { agenda.append(state({ kind: 'empty', title: 'Sin citas para estos filtros', message: 'Prueba otra fecha o estado.' })); return; }
      const grid = el('div', null, 'pet-grid');
      for (const r of rows) { const card = el('article', null, 'card own-appointment'); card.dataset.vetAppointment = r.id_cita;
        card.append(el('span', APPOINTMENT_STATES[r.estado] || r.estado, 'badge badge-outline'), el('h2', r.nombre_mascota), el('p', `${r.nombre_cliente} ${r.apellido_cliente}`), el('p', r.nombre_servicio), el('p', formatLocalDateTime(r.fecha_inicio)), el('small', 'Hora de Lima'));
        const b = button('Abrir cita y atención', { variant: 'secondary', onClick: () => { if (!writing) loadCase(r.id_cita); } }); b.dataset.action = 'open-vet-case'; b.setAttribute('aria-label', `Abrir cita ${r.id_cita} de ${r.nombre_mascota}`); card.append(b); grid.append(card);
      } agenda.append(grid);
    } catch (error) { if (!signal.aborted && version === listVersion) agenda.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: loadAgenda } })); }
    finally { if (!signal.aborted && version === listVersion) agenda.removeAttribute('aria-busy'); }
  }
  filters.addEventListener('submit', event => { event.preventDefault(); if (!validateForm(filters)) return; if (filters.elements.fecha_desde.value && filters.elements.fecha_hasta.value && filters.elements.fecha_desde.value > filters.elements.fecha_hasta.value) { setFieldError(filters.elements.fecha_hasta, 'La fecha final debe ser igual o posterior a la inicial.'); filters.elements.fecha_hasta.focus(); return; } if (!writing) loadAgenda(); }, { signal });
  filters.addEventListener('reset', () => queueMicrotask(() => { if (!writing) loadAgenda(); }), { signal });
  host.querySelector('[data-vet-refresh]').addEventListener('click', () => { if (!writing) loadAgenda(); }, { signal });
  function section(title, key) { const s = el('section', null, 'card vet-section'); s.dataset.clinicalSection = key; s.append(el('h2', title)); caseHost.append(s); return s; }
  function addEdit(host, label, kind, ctx, record) { const b = button(label, { variant: 'secondary', onClick: () => { if (!writing) openEditor(kind, ctx, record); } }); b.dataset.clinicalAction = kind; if (record) b.dataset.clinicalRecord = record[{ atencion:'id_atencion', triaje:'id_triaje', consulta:'id_consulta', receta:'id_receta', detalle:'id_detalle', vacuna:'id_vacuna' }[kind]]; host.append(b); }
  async function changeState(cita, next, control) {
    if (writing) return;
    if (!editor.hidden) { notify('Guarda o cancela el formulario abierto antes de cambiar el estado.', { key: 'vet-result' }); return; }
    await withBusy(control, async () => {
      if (!await confirmDialog({ title: next === 'ATENDIDA' ? 'Finalizar atención' : 'Actualizar cita', message: next === 'ATENDIDA' ? `Se finalizará la cita ${cita.id_cita} con los datos guardados. Después no podrás modificar sus registros clínicos. FastAPI exige atención, triaje y consulta.` : `La cita ${cita.id_cita} pasará a ${APPOINTMENT_STATES[next]}.`, confirmLabel: next === 'ATENDIDA' ? 'Finalizar atención' : 'Confirmar cambio', signal }) || signal.aborted) return;
      writing = true;
      try { await api.changeState(cita.id_cita, next, { signal }); if (signal.aborted) return; notify('Estado actualizado.', { tone: 'success', key: 'vet-result' }); await loadAgenda(); await loadCase(cita.id_cita); }
      catch (error) { if (!signal.aborted) { caseHost.querySelector('[data-clinical-error]')?.remove(); const s = state({ kind: 'error', title: 'No se pudo cambiar el estado', message: errorMessage(error) }); s.dataset.clinicalError = ''; caseHost.prepend(s); } }
      finally { writing = false; }
    });
  }
  async function loadCase(id) {
    closeEditor(); const version = ++caseVersion; selected = id; caseHost.hidden = false; caseHost.setAttribute('aria-busy', 'true'); caseHost.replaceChildren(state({ kind: 'loading', title: 'Consultando cita y registros clínicos…' }));
    try {
      const cita = await api.appointment(id, { signal });
      if (signal.aborted || version !== caseVersion) return;
      const attention = await optional(api.attention(id, { signal }));
      let triage = null, consultation = null, prescriptions = [], vaccines = [], details = new Map();
      if (attention) [triage, consultation] = await Promise.all([optional(api.triage(attention.id_atencion, { signal })), optional(api.consultation(attention.id_atencion, { signal }))]);
      if (consultation) { [prescriptions, vaccines] = await Promise.all([api.prescriptions(consultation.id_consulta, { signal }), api.vaccines(consultation.id_consulta, { signal })]); const groups = await Promise.all(prescriptions.map(r => api.details(r.id_receta, { signal }))); details = new Map(prescriptions.map((r, i) => [r.id_receta, groups[i]])); }
      if (signal.aborted || version !== caseVersion) return;
      caseHost.replaceChildren(); const h = el('h2', `Cita ${id} · ${APPOINTMENT_STATES[cita.estado]}`); h.tabIndex = -1; caseHost.append(h); h.focus();
      const info = section('Datos de la cita', 'cita');
      values(info, [['Mascota', `${cita.nombre_mascota} · ${cita.especie_mascota}`], ['Cliente', `${cita.nombre_cliente} ${cita.apellido_cliente}`], ['Teléfono de contacto', cita.telefono_cliente], ['Servicio', cita.nombre_servicio], ['Inicio · Lima', formatLocalDateTime(cita.fecha_inicio)], ['Fin · Lima', formatLocalDateTime(cita.fecha_fin)], ['Motivo', cita.motivo]]);
      const actions = el('div', null, 'button-row');
      const history = el('a', 'Ver historial de la mascota', 'button button-secondary'); history.href = `#/veterinario/historial?id_mascota=${cita.id_mascota}`; history.dataset.action = 'vet-history'; actions.append(history);
      const target = { PROGRAMADA: ['CONFIRMADA', 'Confirmar cita'], CONFIRMADA: ['EN_ATENCION', 'Iniciar atención'], EN_ATENCION: ['ATENDIDA', 'Finalizar atención'] }[cita.estado];
      if (target) { const b = button(target[1], { onClick: () => changeState(cita, target[0], b) }); b.dataset.action = 'vet-state'; b.dataset.nextState = target[0]; actions.append(b); }
      const refresh = button('Actualizar atención', { variant: 'secondary', onClick: () => { if (!writing) loadCase(id); } }); refresh.dataset.action = 'refresh-case'; actions.append(refresh); info.append(actions);
      const writable = cita.estado === 'EN_ATENCION';
      const status = el('p', writable ? 'Edición habilitada mientras la cita esté EN_ATENCION. El servidor revalida cada operación.' : 'Registros de solo lectura en el estado actual.', 'client-note'); status.dataset.clinicalMode = writable ? 'write' : 'read'; caseHost.append(status);
      const att = section('Atención', 'atencion');
      if (attention) { values(att, [['Fecha de atención', formatLocalDateTime(attention.fecha_atencion)], ['Observaciones', attention.observaciones]]); att.append(el('p', 'La atención inicial no dispone de edición.', 'client-note')); }
      else { att.append(el('p', 'Sin atención registrada.', 'client-note')); if (writable) addEdit(att, 'Registrar atención', 'atencion', { id_cita: id }); }
      const tri = section('Triaje', 'triaje'), con = section('Consulta', 'consulta');
      for (const [host, kind, record] of [[tri, 'triaje', triage], [con, 'consulta', consultation]]) {
        if (record) clinicalValues(host, kind, record); else host.append(el('p', attention ? 'Sin registrar.' : 'Primero registra la atención.', 'client-note'));
        if (writable && attention) addEdit(host, record ? 'Editar '+CLINICAL_TITLES[kind].toLowerCase() : 'Registrar '+CLINICAL_TITLES[kind].toLowerCase(), kind, { id_atencion: attention.id_atencion }, record);
      }
      const rx = section('Recetas y medicamentos', 'receta'), va = section('Vacunas', 'vacuna');
      if (!consultation) { rx.append(el('p', 'Primero registra la consulta.', 'client-note')); va.append(el('p', 'Primero registra la consulta.', 'client-note')); }
      else {
        const ctx = { id_consulta: consultation.id_consulta };
        if (writable) { addEdit(rx, 'Nueva receta', 'receta', ctx); addEdit(va, 'Registrar vacuna', 'vacuna', ctx); }
        if (!prescriptions.length) rx.append(el('p', 'Sin recetas registradas.', 'client-note'));
        for (const r of prescriptions) {
          const article = el('article', null, 'vet-prescription'); article.dataset.prescriptionId = r.id_receta; article.append(el('h3', `Receta ${r.id_receta}`)); clinicalValues(article, 'receta', r);
          if (writable) { addEdit(article, 'Editar receta', 'receta', ctx, r); addEdit(article, 'Añadir medicamento', 'detalle', { id_receta: r.id_receta }); }
          const items = details.get(r.id_receta);
          if (!items.length) article.append(el('p', 'Sin medicamentos registrados.', 'client-note'));
          for (const d of items) { const item = el('section', null, 'vet-medicine'); item.dataset.detailId = d.id_detalle; item.append(el('h4', d.medicamento)); clinicalValues(item, 'detalle', d); if (writable) addEdit(item, 'Editar medicamento', 'detalle', { id_receta: r.id_receta }, d); article.append(item); }
          rx.append(article);
        }
        if (!vaccines.length) va.append(el('p', 'Sin vacunas registradas.', 'client-note'));
        for (const v of vaccines) { const article = el('article', null, 'vet-prescription'); article.dataset.vaccineId = v.id_vacuna; article.append(el('h3', v.nombre_vacuna)); clinicalValues(article, 'vacuna', v); if (writable) addEdit(article, 'Editar vacuna', 'vacuna', ctx, v); va.append(article); }
      }
    } catch (error) { if (!signal.aborted && version === caseVersion) caseHost.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: () => loadCase(id) } })); }
    finally { if (!signal.aborted && version === caseVersion) caseHost.removeAttribute('aria-busy'); }
  }
  function openEditor(kind, ctx, record) {
    closeEditor(); editorController = new AbortController(); const local = editorController.signal;
    const caseId = selected; editor.hidden = false; const h = el('h2', `${record ? 'Editar' : 'Registrar'} ${CLINICAL_TITLES[kind].toLowerCase()}`); h.tabIndex = -1; editor.append(h);
    const form = el('form'); form.noValidate = true; form.dataset.clinicalForm = kind;
    const alert = el('div', null, 'auth-error'); alert.hidden = true; alert.setAttribute('role', 'alert'); alert.tabIndex = -1;
    const grid = el('div', null, 'client-form-grid');
    for (const f of CLINICAL_FIELDS[kind]) { const group = field({ ...f, id: `clinical-${kind}-${f.name}`, hint: f.required ? '' : 'Opcional.' }); group.querySelector('input,textarea').value = record?.[f.name] ?? ''; grid.append(group); }
    const actions = el('div', null, 'button-row'), save = button('Guardar', { type: 'submit' }); save.dataset.action = 'save-clinical';
    const cancel = button('Cancelar', { variant: 'secondary', onClick: () => { if (!writing) { closeEditor(); caseHost.querySelector('h2')?.focus(); } } }); actions.append(save, cancel); form.append(alert, grid, actions); editor.append(form); h.focus();
    form.addEventListener('input', e => setFieldError(e.target), { signal: local });
    form.addEventListener('submit', async event => {
      event.preventDefault(); if (writing || local.aborted) return;
      for (const input of form.querySelectorAll('input,textarea')) input.value = input.value.trim();
      if (!validateForm(form)) return;
      if (kind === 'vacuna' && form.elements.proxima_dosis.value && form.elements.proxima_dosis.value < form.elements.fecha_aplicacion.value) { setFieldError(form.elements.proxima_dosis, 'La próxima dosis no puede ser anterior a la aplicación.'); form.elements.proxima_dosis.focus(); return; }
      await withBusy(save, async () => {
        if (record && !await confirmDialog({ title: 'Guardar cambios clínicos', message: 'Se actualizará el registro de esta cita.', confirmLabel: 'Guardar cambios', signal: local }) || local.aborted) return;
        writing = true; cancel.disabled = true;
        try { await api.save(kind, ctx, Object.fromEntries(new FormData(form)), record, { signal: local }); if (local.aborted || signal.aborted) return; notify('Registro clínico guardado.', { tone: 'success', key: 'vet-result' }); await loadCase(caseId); }
        catch (error) { if (!local.aborted && !signal.aborted) { alert.hidden = false; alert.textContent = errorMessage(error); for (const f of error.fields || []) if (form.elements[f.field]) setFieldError(form.elements[f.field], f.message); alert.focus(); } }
        finally { writing = false; cancel.disabled = false; }
      });
    }, { signal: local });
  }
  signal.addEventListener('abort', () => { caseVersion++; closeEditor(); caseHost.replaceChildren(); }, { once: true });
  loadAgenda();
  const id = Number(new URLSearchParams(window.location.hash.split('?')[1] || '').get('id_cita'));
  if (Number.isSafeInteger(id) && id > 0) loadCase(id);
}
