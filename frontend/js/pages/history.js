import { historyApi as api } from '../api/history.js';
import { getSession } from '../core/session.js';
import { field, validateForm } from '../components/forms.js';
import { button } from '../components/buttons.js';
import { state } from '../components/states.js';
import { errorMessage } from '../core/errors.js';
import { formatLocalDateTime } from '../adapters/dates.js';
import { petDate } from '../adapters/pets.js';

const el = (tag, text, cls) => { const node = document.createElement(tag); if (text != null) node.textContent = text; if (cls) node.className = cls; return node; };
function values(host, pairs) {
  const dl = el('dl', null, 'client-detail-grid');
  for (const [label, value] of pairs) dl.append(el('dt', label), el('dd', value == null || value === '' ? 'Sin registrar' : value));
  host.append(dl);
}
function section(host, title, key) { const node = el('section', null, 'card history-section'); node.dataset.historySection = key; node.append(el('h3', title)); host.append(node); return node; }
export function mountHistory({ host, signal }) {
  const role = getSession()?.user.id_rol; if (![1, 2, 3].includes(role)) return;
  const picker = host.querySelector('[data-history-selector]'), results = host.querySelector('[data-history-results]'), detail = host.querySelector('[data-history-detail]');
  host.querySelector('[data-history-scope]').textContent = {
    1: 'Selecciona una mascota del listado administrativo de mascotas activas. Consulta en modo lectura.',
    2: 'Selecciona una mascota de tu agenda. Puedes consultar su historial completo si tiene alguna cita asignada a ti, incluidas atenciones de otros profesionales.',
    3: 'Selecciona una de tus mascotas activas. Solo puedes consultar historiales de mascotas propias.',
  }[role];
  let petController, detailController, petVersion = 0, detailVersion = 0;
  function clearDetail() { detailController?.abort(); detailVersion++; detail.replaceChildren(); detail.hidden = true; detail.removeAttribute('aria-busy'); }
  signal.addEventListener('abort', () => { petController?.abort(); clearDetail(); results.replaceChildren(); picker.replaceChildren(); }, { once: true });
  async function loadPets() {
    picker.setAttribute('aria-busy', 'true'); picker.replaceChildren(state({ kind: 'loading', title: 'Consultando mascotas disponibles…' }));
    try {
      const pets = await api.pets(role, { signal }); if (signal.aborted) return;
      picker.replaceChildren();
      if (!pets.length) { picker.append(state({ kind: 'empty', title: 'Sin mascotas para seleccionar', message: role === 2 ? 'Tu agenda no contiene mascotas asignadas.' : 'No hay mascotas activas en este listado.' })); return; }
      const form = el('form'); form.noValidate = true; form.dataset.historyForm = '';
      form.append(field({ id: 'history-pet', name: 'id_mascota', type: 'select', label: 'Mascota', required: true, options: [{ value: '', label: 'Selecciona una mascota' }, ...pets.map(p => ({ value: p.id_mascota, label: `${p.nombre} · ${p.especie}` }))] }));
      const actions = el('div', null, 'button-row'); actions.append(button('Consultar historial', { type: 'submit' })); form.append(actions); picker.append(form);
      form.addEventListener('submit', event => { event.preventDefault(); if (validateForm(form)) loadHistory(Number(form.elements.id_mascota.value)); }, { signal });
    } catch (error) { if (!signal.aborted) picker.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar selección', onClick: loadPets } })); }
    finally { if (!signal.aborted) picker.removeAttribute('aria-busy'); }
  }
  async function loadHistory(pet, attention) {
    petController?.abort(); petController = new AbortController(); const local = petController.signal, version = ++petVersion;
    clearDetail(); results.setAttribute('aria-busy', 'true'); results.replaceChildren(state({ kind: 'loading', title: 'Consultando historial clínico…' }));
    try {
      const history = await api.list(pet, { signal: local }); if (signal.aborted || local.aborted || version !== petVersion) return;
      results.replaceChildren(); const heading = el('h2', history.mascota.nombre); heading.tabIndex = -1; results.append(heading, el('p', `${history.mascota.especie} · ${history.mascota.raza || 'Raza sin registrar'}`, 'client-note'));
      results.append(el('p', 'De la atención más reciente a la más antigua · Hora de Lima', 'client-note'));
      const select = picker.querySelector('select'); if (select && [...select.options].some(o => Number(o.value) === pet)) select.value = pet;
      if (!history.atenciones.length) results.append(state({ kind: 'empty', title: 'Esta mascota aún no tiene atenciones registradas', message: 'Aquí aparecerá su información clínica cuando exista una atención.' }));
      else {
        const timeline = el('ol', null, 'history-timeline');
        for (const row of history.atenciones) {
          const item = el('li'), card = el('article', null, 'card history-entry'); card.dataset.historyAttention = row.id_atencion;
          card.append(el('p', formatLocalDateTime(row.fecha_atencion), 'history-date'), el('h3', `Atención ${row.id_atencion}`), el('p', `${row.nombre_veterinario} ${row.apellido_veterinario}`, 'history-professional'), el('small', row.especialidad));
          values(card, [['Diagnóstico', row.diagnostico], ['Tratamiento', row.tratamiento]]);
          const open = button('Ver atención completa', { variant: 'secondary', onClick: () => loadDetail(pet, row.id_atencion) }); open.dataset.action = 'history-detail'; open.setAttribute('aria-label', `Ver atención ${row.id_atencion} del ${formatLocalDateTime(row.fecha_atencion)}`); card.append(open); item.append(card); timeline.append(item);
        } results.append(timeline);
      }
      heading.focus();
      if (attention) loadDetail(pet, attention);
    } catch (error) { if (!signal.aborted && !local.aborted && version === petVersion) results.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar historial', onClick: () => loadHistory(pet, attention) } })); }
    finally { if (!signal.aborted && !local.aborted && version === petVersion) results.removeAttribute('aria-busy'); }
  }
  async function loadDetail(pet, attention) {
    clearDetail(); detailController = new AbortController(); const local = detailController.signal, version = detailVersion;
    detail.hidden = false; detail.setAttribute('aria-busy', 'true'); detail.append(state({ kind: 'loading', title: 'Consultando atención completa…' }));
    try {
      const row = await api.detail(pet, attention, { signal: local }); if (signal.aborted || local.aborted || version !== detailVersion) return;
      detail.replaceChildren(); const heading = el('h2', `Atención ${row.id_atencion} · ${formatLocalDateTime(row.fecha_atencion)}`); heading.tabIndex = -1;
      detail.append(heading, el('p', 'Información clínica de solo lectura · Hora de Lima', 'client-note'));
      const general = section(detail, 'Atención y profesional', 'atencion');
      values(general, [['Veterinario', `${row.nombre_veterinario} ${row.apellido_veterinario}`], ['Especialidad', row.especialidad], ['Fecha de cita', formatLocalDateTime(row.fecha_cita)], ['Observaciones de atención', row.observaciones_atencion]]);
      const triage = section(detail, 'Triaje', 'triaje');
      values(triage, [['Peso', row.peso], ['Temperatura', row.temperatura], ['Frecuencia cardíaca', row.frecuencia_cardiaca], ['Frecuencia respiratoria', row.frecuencia_respiratoria], ['Observaciones', row.observaciones_triaje]]);
      const consultation = section(detail, 'Consulta', 'consulta');
      values(consultation, [['Diagnóstico', row.diagnostico], ['Tratamiento', row.tratamiento], ['Observaciones', row.observaciones_consulta]]);
      const recipes = section(detail, 'Recetas y medicamentos', 'recetas');
      if (!row.recetas.length) recipes.append(el('p', 'Sin recetas registradas.', 'client-note'));
      for (const recipe of row.recetas) {
        const article = el('article', null, 'history-prescription'); article.dataset.historyPrescription = recipe.id_receta; article.append(el('h4', `Receta ${recipe.id_receta}`));
        values(article, [['Emisión', formatLocalDateTime(recipe.fecha_emision)], ['Indicaciones', recipe.indicaciones]]);
        if (!recipe.detalles.length) article.append(el('p', 'Sin medicamentos registrados.', 'client-note'));
        for (const medicine of recipe.detalles) {
          const item = el('section', null, 'history-medicine'); item.dataset.historyMedicine = medicine.id_detalle; item.append(el('h5', medicine.medicamento));
          values(item, [['Dosis', medicine.dosis], ['Frecuencia', medicine.frecuencia], ['Duración', medicine.duracion], ['Indicaciones', medicine.indicaciones]]); article.append(item);
        } recipes.append(article);
      }
      const vaccines = section(detail, 'Vacunas', 'vacunas');
      if (!row.vacunas.length) vaccines.append(el('p', 'Sin vacunas registradas.', 'client-note'));
      for (const vaccine of row.vacunas) {
        const article = el('article', null, 'history-prescription'); article.dataset.historyVaccine = vaccine.id_vacuna; article.append(el('h4', vaccine.nombre_vacuna));
        values(article, [['Aplicación', petDate(vaccine.fecha_aplicacion)], ['Próxima dosis', petDate(vaccine.proxima_dosis)], ['Observaciones', vaccine.observaciones]]); vaccines.append(article);
      }
      detail.append(button('Cerrar atención', { variant: 'secondary', onClick: () => { clearDetail(); const opener = results.querySelector(`[data-history-attention="${attention}"] button`); opener?.focus(); } }));
      heading.focus(); heading.scrollIntoView({ block: 'start' });
    } catch (error) { if (!signal.aborted && !local.aborted && version === detailVersion) detail.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar atención', onClick: () => loadDetail(pet, attention) } })); }
    finally { if (!signal.aborted && !local.aborted && version === detailVersion) detail.removeAttribute('aria-busy'); }
  }
  results.append(state({ kind: 'empty', title: 'Selecciona una mascota para consultar su historial', message: 'Las consultas no modifican sus registros clínicos.' }));
  loadPets();
  const query = new URLSearchParams(window.location.hash.split('?')[1] || ''), pet = Number(query.get('id_mascota')), attention = Number(query.get('id_atencion'));
  if (Number.isSafeInteger(pet) && pet > 0) loadHistory(pet, Number.isSafeInteger(attention) && attention > 0 ? attention : undefined);
}
