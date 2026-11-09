import { petsApi } from '../api/pets.js';
import { PET_FIELDS, PET_SEX, petDate } from '../adapters/pets.js';
import { getSession } from '../core/session.js';
import { button, withBusy } from '../components/buttons.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { state } from '../components/states.js';
import { confirmDialog } from '../components/dialog.js';
import { notify } from '../components/feedback.js';
import { icon } from '../components/icons.js';
import { errorMessage } from '../core/errors.js';

function el(tag, text, className) { const n = document.createElement(tag); if (text != null) n.textContent = text; if (className) n.className = className; return n; }
function title(host, text) { const h = el('h2', text); h.tabIndex = -1; host.append(h); h.focus(); }
function petCard(pet, actions) {
  const card = el('article', null, 'card pet-card'); card.dataset.petId = pet.id_mascota;
  const mark = el('span', null, 'icon-tile'); mark.append(icon('heart'));
  card.append(mark, el('h2', pet.nombre), el('p', pet.especie, 'pet-species'), el('p', pet.raza || 'Raza sin registrar', 'pet-meta'));
  if (actions) card.append(actions(pet));
  else { const link = el('a', 'Ver mascota →', 'text-link'); link.href = `#/cliente/mascotas?id_mascota=${pet.id_mascota}`; card.append(link); }
  return card;
}
export function mountClient({ host, signal, route }) {
  const session = getSession(); if (session?.user.id_rol !== 3) return;
  const profile = session.profile || {};
  if (route.page === 'clientProfile') {
    const dl = host.querySelector('[data-client-profile-fields]');
    for (const [key, label] of [['nombre', 'Nombre'], ['apellido', 'Apellido'], ['correo', 'Correo electrónico']]) dl.append(el('dt', label), el('dd', profile[key] || 'No disponible'));
    return;
  }
  if (route.page === 'clientPanel') {
    host.querySelector('[data-client-welcome]').textContent = profile.nombre ? `Hola, ${profile.nombre}` : 'Bienvenido a tu espacio';
    host.querySelector('[data-client-name]').textContent = [profile.nombre, profile.apellido].filter(Boolean).join(' ') || 'Cuenta de cliente';
    host.querySelector('[data-client-email]').textContent = profile.correo || 'Correo no disponible';
    host.querySelector('[data-client-heart]').append(icon('heart'));
    const slot = host.querySelector('[data-client-pets]'), count = host.querySelector('[data-pet-count]');
    async function load() {
      slot.replaceChildren(state({ kind: 'loading', title: 'Consultando tus mascotas…' }));
      try {
        const rows = await petsApi.list({ signal }); if (signal.aborted) return;
        count.textContent = String(rows.length);
        if (!rows.length) slot.replaceChildren(state({ kind: 'empty', title: 'Aquí empieza su historia', message: 'Todavía no tienes mascotas activas. Registra la primera desde Mis mascotas.' }));
        else { const cards = el('div', null, 'pet-grid'); for (const pet of rows.slice(0, 3)) cards.append(petCard(pet)); slot.replaceChildren(cards); }
      } catch (error) { if (!signal.aborted) { count.textContent = 'No disponible'; slot.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: load } })); } }
    }
    load(); return;
  }
  mountPets({ host, signal });
}

function mountPets({ host, signal }) {
  const slot = host.querySelector('[data-pet-list]'), count = host.querySelector('[data-pet-count]');
  const editor = host.querySelector('[data-pet-editor]'), detail = host.querySelector('[data-pet-detail]');
  const tools = host.querySelector('[data-pet-tools]');
  const searchField = field({ id: 'pet-search', name: 'search', type: 'search', label: 'Buscar entre mis mascotas', hint: 'Por nombre, especie o raza.' }); host.querySelector('[data-pet-search]').append(searchField);
  const search = searchField.querySelector('input');
  let rows = [], dataReady = false, generation = 0, interaction = 0, writing = false;
  const options = { signal };
  const create = button('Registrar mascota', { onClick: () => { if (!writing) edit(); } }); create.dataset.action = 'create-pet';
  const refresh = button('Actualizar', { variant: 'secondary', onClick: () => { if (!writing) load(); } }); tools.append(refresh, create);
  function close() { interaction++; editor.hidden = true; editor.replaceChildren(); detail.hidden = true; detail.replaceChildren(); }
  function render() {
    if (signal.aborted || !dataReady) return;
    const term = search.value.trim().toLocaleLowerCase('es');
    const visible = rows.filter(p => [p.nombre, p.especie, p.raza].some(v => String(v || '').toLocaleLowerCase('es').includes(term)));
    count.textContent = `${visible.length} de ${rows.length} mascotas activas`;
    if (!visible.length) { slot.replaceChildren(state({ kind: 'empty', title: rows.length ? 'Sin coincidencias' : 'Sin mascotas activas', message: rows.length ? 'Prueba otro nombre, especie o raza.' : 'Puedes registrar una mascota con el botón superior.' })); return; }
    const cards = el('div', null, 'pet-grid');
    for (const pet of visible) cards.append(petCard(pet, row => {
      const actions = el('div', null, 'button-row pet-actions');
      for (const [label, action, fn] of [['Ver', 'view-pet', () => show(row.id_mascota)], ['Editar', 'edit-pet', () => edit(row.id_mascota)], ['Desactivar', 'deactivate-pet', b => deactivate(row, b)]]) {
        const b = button(label, { variant: 'secondary', onClick: () => { if (!writing) fn(b); } }); b.dataset.action = action; b.setAttribute('aria-label', `${label}: ${row.nombre}`); actions.append(b);
      }
      return actions;
    })); slot.replaceChildren(cards);
  }
  search.addEventListener('input', render, options);
  async function load() {
    const version = ++generation; dataReady = false; count.textContent = ''; refresh.disabled = true;
    slot.setAttribute('aria-busy', 'true'); slot.replaceChildren(state({ kind: 'loading', title: 'Consultando tus mascotas…' }));
    try { const result = await petsApi.list(options); if (signal.aborted || version !== generation) return; rows = result; dataReady = true; render(); }
    catch (error) { if (!signal.aborted && version === generation) slot.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: load } })); }
    finally { if (!signal.aborted && version === generation) { refresh.disabled = false; slot.removeAttribute('aria-busy'); } }
  }
  async function show(id) {
    close(); const version = interaction; detail.hidden = false; detail.append(state({ kind: 'loading', title: 'Consultando mascota…' }));
    try {
      const pet = await petsApi.get(id, options); if (signal.aborted || version !== interaction) return;
      detail.replaceChildren(); title(detail, pet.nombre);
      const dl = el('dl', null, 'client-detail-grid');
      for (const f of PET_FIELDS.filter(f => f.name !== 'nombre')) {
        const value = f.name === 'sexo' ? PET_SEX[pet.sexo] || 'No especificado' : f.name === 'fecha_nacimiento' ? petDate(pet.fecha_nacimiento) : pet[f.name] ?? 'Sin registrar';
        dl.append(el('dt', f.label.replace(' (opcional)', '')), el('dd', value));
      }
      const history = el('a', 'Ver historial clínico', 'button button-secondary'); history.href = `#/cliente/historial?id_mascota=${pet.id_mascota}`;
      detail.append(dl, history, button('Cerrar detalle', { variant: 'secondary', onClick: () => { close(); search.focus(); } }));
    } catch (error) { if (!signal.aborted && version === interaction) detail.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); }
  }
  async function edit(id) {
    close(); const version = interaction; editor.hidden = false; editor.append(state({ kind: 'loading', title: 'Preparando formulario…' }));
    try {
      const pet = id ? await petsApi.get(id, options) : null; if (signal.aborted || version !== interaction) return;
      editor.replaceChildren(); title(editor, pet ? `Editar a ${pet.nombre}` : 'Registrar mascota');
      const form = el('form'); form.noValidate = true; form.dataset.petForm = '';
      const alert = el('div', null, 'auth-error'); alert.hidden = true; alert.setAttribute('role', 'alert'); alert.tabIndex = -1;
      const grid = el('div', null, 'client-form-grid');
      for (const f of PET_FIELDS) { const group = field({ ...f, id: `pet-${f.name}` }); group.querySelector('input,select').value = pet?.[f.name] ?? (f.name === 'sexo' ? 'NO_ESPECIFICADO' : ''); grid.append(group); }
      const save = button('Guardar mascota', { type: 'submit' }); save.dataset.action = 'save-pet';
      const cancel = button('Cancelar', { variant: 'secondary', onClick: () => { if (!writing) { close(); create.focus(); } } });
      const actions = el('div', null, 'button-row'); actions.append(save, cancel); form.append(alert, grid, actions); editor.append(form);
      form.addEventListener('input', e => setFieldError(e.target), options);
      form.addEventListener('submit', async event => {
        event.preventDefault(); if (writing || signal.aborted) return;
        for (const input of form.querySelectorAll('input')) input.value = input.value.trim();
        if (!validateForm(form)) return;
        await withBusy(save, async () => {
          if (pet && !await confirmDialog({ title: 'Guardar cambios de mascota', message: `Se actualizarán los datos de ${pet.nombre}.`, confirmLabel: 'Guardar cambios', signal })) return;
          if (signal.aborted) return;
          writing = true; cancel.disabled = true;
          try {
            const values = Object.fromEntries(new FormData(form));
            if (pet) await petsApi.update(pet.id_mascota, values, options); else await petsApi.create(values, options);
            if (signal.aborted) return;
            close(); notify('Información de mascota guardada.', { tone: 'success', key: 'client-result' }); await load(); create.focus();
          } catch (error) {
            if (signal.aborted) return;
            alert.textContent = errorMessage(error); alert.hidden = false; alert.focus();
            for (const f of error.fields || []) if (form.elements[f.field]) setFieldError(form.elements[f.field], f.message);
          } finally { writing = false; cancel.disabled = false; }
        });
      }, options);
    } catch (error) { if (!signal.aborted && version === interaction) editor.replaceChildren(state({ kind: 'error', message: errorMessage(error) })); }
  }
  async function deactivate(pet, control) {
    if (writing || document.querySelector('dialog[open]')) return;
    await withBusy(control, async () => {
      if (!await confirmDialog({ title: 'Desactivar mascota', message: `${pet.nombre} dejará de aparecer entre tus mascotas activas. Esta pantalla no permite reactivarla.`, confirmLabel: 'Desactivar mascota', signal }) || signal.aborted) return;
      writing = true;
      try { await petsApi.deactivate(pet.id_mascota, options); if (signal.aborted) return; close(); notify('Mascota desactivada.', { tone: 'success', key: 'client-result' }); await load(); create.focus(); }
      catch (error) { if (!signal.aborted) notify(errorMessage(error), { tone: 'error', key: 'client-result' }); }
      finally { writing = false; }
    });
  }
  signal.addEventListener('abort', () => { editor.querySelector('form')?.reset(); close(); }, { once: true });
  load().then(() => { if (!signal.aborted) { const value = new URLSearchParams(window.location.hash.split('?')[1] || '').get('id_mascota'); if (value && Number.isSafeInteger(Number(value)) && Number(value) > 0) show(Number(value)); } });
}
