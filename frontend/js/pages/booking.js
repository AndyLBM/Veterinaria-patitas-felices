import { clientAppointmentsApi as api } from '../api/client-appointments.js';
import { petsApi } from '../api/pets.js';
import { startCivil, endCivil, fitsAvailability } from '../adapters/booking.js';
import { formatLocalDateTime } from '../adapters/dates.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { button, withBusy } from '../components/buttons.js';
import { confirmDialog } from '../components/dialog.js';
import { state } from '../components/states.js';
import { errorMessage } from '../core/errors.js';
import { getSession } from '../core/session.js';

const el = (tag, text, cls) => { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; };
export function mountClientBooking({ host, signal }) { if (getSession()?.user.id_rol === 3) mountBookingForm({ host: host.querySelector('[data-booking-host]'), signal }); }

export async function mountBookingForm({ host, signal, appointment, onSaved }) {
  if (getSession()?.user.id_rol !== 3) return;
  const moving = Boolean(appointment);
  host.replaceChildren(state({ kind: 'loading', title: 'Preparando tu cita…' }));
  let pets = [], services = [];
  try {
    if (!moving) [pets, services] = await Promise.all([petsApi.list({ signal }), api.services({ signal })]);
    if (signal.aborted) return;
  } catch (error) { if (!signal.aborted) host.replaceChildren(state({ kind: 'error', message: errorMessage(error), action: { label: 'Reintentar', onClick: () => mountBookingForm({ host, signal, appointment, onSaved }) } })); return; }
  host.replaceChildren();
  if (!moving && (!pets.length || !services.length)) {
    host.append(state({ kind: 'empty', title: !pets.length ? 'Primero registra una mascota' : 'Sin servicios activos', message: !pets.length ? 'Necesitas una mascota propia y activa para reservar.' : 'Consulta más adelante los servicios disponibles.' }));
    if (!pets.length) { const link = el('a', 'Ir a Mis mascotas', 'button'); link.href = '#/cliente/mascotas'; host.append(link); } return;
  }
  const form = el('form'); form.noValidate = true; form.dataset.reservationForm = moving ? 'reprogram' : 'create';
  const base = el('div', null, 'client-form-grid');
  function control(container, spec) { const group = field({ ...spec, id: `reserve-${spec.name}` }); container.append(group); return group.querySelector('input,select,textarea'); }
  let pet, service;
  if (moving) {
    host.append(el('h2', 'Reprogramar cita'), el('p', `${appointment.nombre_mascota} · ${appointment.nombre_servicio} · ${appointment.duracion_minutos} minutos`, 'client-note'), el('p', 'Por ahora puedes cambiar fecha y hora con el veterinario actual. El cambio de veterinario queda pendiente.', 'client-note'));
  } else {
    pet = control(base, { name: 'id_mascota', label: 'Mascota', type: 'select', required: true, options: [{ value: '', label: 'Selecciona tu mascota' }, ...pets.map(p => ({ value: String(p.id_mascota), label: p.nombre }))] });
    service = control(base, { name: 'id_servicio', label: 'Servicio', type: 'select', required: true, options: [{ value: '', label: 'Selecciona un servicio' }, ...services.map(s => ({ value: String(s.id_servicio), label: `${s.nombre} · ${s.duracion_minutos} min` }))] });
  }
  const date = control(base, { name: 'fecha', label: 'Fecha · Lima', type: 'date', required: true });
  if (moving) date.value = appointment.fecha_inicio.slice(0, 10);
  const reason = moving ? null : control(base, { name: 'motivo', label: 'Motivo (opcional)', type: 'textarea' });
  const vetGroup = el('div');
  const vet = control(vetGroup, { name: 'id_veterinario', label: 'Veterinario', type: 'select', required: true, options: moving ? [{ value: String(appointment.id_veterinario), label: `${appointment.nombre_veterinario} ${appointment.apellido_veterinario}` }] : [{ value: '', label: 'Consulta primero los veterinarios' }] });
  if (moving) vet.disabled = true;
  const lookupVets = moving ? null : button('Consultar veterinarios', { onClick: () => findVets() });
  if (lookupVets) lookupVets.dataset.action = 'lookup-vets';
  const lookup = button('Consultar horarios', { variant: 'secondary', onClick: () => findAvailability() }); lookup.dataset.action = 'lookup-availability';
  const slots = el('section', null, 'booking-availability'); slots.setAttribute('aria-live', 'polite');
  const summary = el('section', null, 'booking-summary'); summary.hidden = true; summary.dataset.bookingSummary = '';
  const alert = el('div', null, 'auth-error'); alert.hidden = true; alert.setAttribute('role', 'alert'); alert.tabIndex = -1;
  const save = button(moving ? 'Revisar reprogramación' : 'Revisar y confirmar', { type: 'submit' }); save.dataset.action = 'review-booking'; save.disabled = true;
  form.append(base); if (lookupVets) form.append(lookupVets); form.append(vetGroup, lookup, slots, summary, alert, save); host.append(form);
  let availability, interval, time, vets = moving ? [{ id_veterinario: appointment.id_veterinario, nombre: appointment.nombre_veterinario, apellido: appointment.apellido_veterinario }] : [], revision = 0, request, writing = false;
  const context = () => `${pet?.value || appointment?.id_mascota}|${service?.value || appointment?.id_servicio}|${date.value}|${vet.value}`;
  function invalidate(resetVets = false) {
    revision++; request?.abort(); availability = null; save.disabled = true; summary.hidden = true; slots.replaceChildren(); alert.hidden = true;
    if (resetVets && !moving) { vet.replaceChildren(); const option = el('option', 'Consulta primero los veterinarios'); option.value = ''; vet.append(option); vets = []; }
  }
  for (const input of [pet, service, date].filter(Boolean)) input.addEventListener('change', () => invalidate(true), { signal });
  vet.addEventListener('change', () => invalidate(), { signal });
  function begin() { request?.abort(); request = new AbortController(); return { signal: request.signal }; }
  function showError(error) { alert.hidden = false; alert.textContent = errorMessage(error); alert.focus(); }
  async function findVets() {
    if (writing || !validateForm(base)) return;
    invalidate(true); const key = context(), version = revision;
    await withBusy(lookupVets, async () => {
      slots.replaceChildren(state({ kind: 'loading', title: 'Buscando veterinarios…' }));
      try {
        const result = await api.vets(service.value, date.value, begin());
        if (signal.aborted || revision !== version || context() !== key) return;
        vets = result; vet.replaceChildren(); const blank = el('option', 'Selecciona un veterinario'); blank.value = ''; vet.append(blank);
        for (const v of vets) { const o = el('option', `${v.nombre} ${v.apellido} · ${v.especialidad}`); o.value = v.id_veterinario; vet.append(o); }
        slots.replaceChildren();
        if (!vets.length) slots.append(state({ kind: 'empty', title: 'Sin veterinarios disponibles', message: 'No hay una franja suficiente para este servicio en la fecha consultada.' })); else vet.focus();
      } catch (error) { if (!signal.aborted && revision === version && error.code !== 'ABORTED') { slots.replaceChildren(); showError(error); } }
    });
  }
  const queryAvailability = options => moving ? api.reprogramAvailability(appointment.id_cita, appointment.id_veterinario, date.value, options) : api.availability(vet.value, service.value, date.value, options);
  async function findAvailability() {
    if (writing || !validateForm(base) || !validateForm(vetGroup)) return;
    invalidate(); const version = revision, key = context();
    await withBusy(lookup, async () => {
      slots.replaceChildren(state({ kind: 'loading', title: 'Consultando disponibilidad…' }));
      try {
        const result = await queryAvailability(begin());
        if (signal.aborted || version !== revision || key !== context()) return;
        availability = result; slots.replaceChildren();
        if (!result.franjas_disponibles.length) { slots.append(state({ kind: 'empty', title: 'Sin horarios disponibles', message: 'Prueba otra fecha o consulta nuevamente.' })); return; }
        slots.append(el('p', `Duración confirmada: ${result.duracion_minutos} minutos · ${result.zona_horaria}`, 'client-note'));
        interval = control(slots, { name: 'franja', label: 'Intervalo disponible', type: 'select', required: true, options: result.franjas_disponibles.map((f, i) => ({ value: String(i), label: `${f.inicio.slice(11)} a ${f.fin.slice(11)}` })) });
        time = control(slots, { name: 'hora', label: 'Hora de inicio · Lima', type: 'time', step: 1, required: true });
        const setStart = () => { time.value = result.franjas_disponibles[Number(interval.value)].inicio.slice(11); summary.hidden = true; };
        interval.addEventListener('change', setStart, { signal }); time.addEventListener('input', () => { summary.hidden = true; setFieldError(time); }, { signal });
        setStart(); slots.append(el('p', 'La disponibilidad puede cambiar. La reserva se confirma al guardarla; el servidor comprueba también las citas de tu mascota.', 'client-note')); save.disabled = false; time.focus();
      } catch (error) { if (!signal.aborted && version === revision && error.code !== 'ABORTED') { slots.replaceChildren(); showError(error); } }
    });
  }
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (writing || save.disabled || !availability || !validateForm(form)) return;
    const start = startCivil(date.value, time.value), selected = availability.franjas_disponibles[Number(interval.value)];
    if (!selected || !fitsAvailability({ ...availability, franjas_disponibles: [selected] }, start)) { setFieldError(time, 'El horario completo debe quedar dentro del intervalo consultado.'); time.focus(); return; }
    const key = context(), version = revision;
    await withBusy(save, async () => {
      writing = true;
      try {
        const fresh = await queryAvailability({ signal });
        if (signal.aborted || key !== context() || version !== revision) return;
        if (!fitsAvailability(fresh, start)) { invalidate(); alert.textContent = 'Este horario ya no está disponible. Consulta nuevamente los horarios.'; alert.hidden = false; alert.focus(); return; }
        const petName = moving ? appointment.nombre_mascota : pets.find(p => p.id_mascota === Number(pet.value))?.nombre;
        const serviceName = moving ? appointment.nombre_servicio : services.find(s => s.id_servicio === Number(service.value))?.nombre;
        const vetInfo = vets.find(v => v.id_veterinario === Number(vet.value));
        const finish = endCivil(start, fresh.duracion_minutos);
        summary.replaceChildren(el('h2', 'Resumen de tu cita'));
        const dl = el('dl', null, 'client-detail-grid');
        for (const [label, value] of [['Mascota', petName], ['Servicio', serviceName], ['Veterinario', `${vetInfo?.nombre || ''} ${vetInfo?.apellido || ''}`], ['Inicio · Lima', formatLocalDateTime(start)], ['Fin · Lima', formatLocalDateTime(finish)], ['Duración', `${fresh.duracion_minutos} minutos`]]) dl.append(el('dt', label), el('dd', value));
        summary.append(dl); summary.hidden = false;
        const accepted = await confirmDialog({ title: moving ? 'Confirmar reprogramación' : 'Confirmar reserva', message: `${petName} · ${serviceName} · ${formatLocalDateTime(start)} (Lima), ${fresh.duracion_minutos} minutos, con ${vetInfo?.nombre || ''} ${vetInfo?.apellido || ''}.`, confirmLabel: moving ? 'Guardar reprogramación' : 'Reservar cita', signal });
        if (!accepted || signal.aborted || key !== context() || version !== revision) return;
        const result = moving ? await api.reprogram(appointment.id_cita, { id_veterinario: appointment.id_veterinario, fecha_inicio: start }, { signal }) : await api.create({ id_mascota: pet.value, id_servicio: service.value, id_veterinario: vet.value, fecha_inicio: start, motivo: reason.value }, { signal });
        if (signal.aborted) return;
        if (onSaved) { await onSaved(result); return; }
        host.replaceChildren(state({ kind: 'empty', title: 'Tu cita está registrada', message: `Cita ${result.id_cita}. ${formatLocalDateTime(start)} · Lima.` }));
        const link = el('a', 'Consultar mi cita', 'button'); link.href = `#/cliente/citas?id_cita=${result.id_cita}`; host.append(link);
      } catch (error) { if (!signal.aborted) { invalidate(); showError(error); } }
      finally { writing = false; if (!availability) save.disabled = true; }
    });
    if (!availability) save.disabled = true;
  }, { signal });
  signal.addEventListener('abort', () => { request?.abort(); form.reset(); }, { once: true });
}
