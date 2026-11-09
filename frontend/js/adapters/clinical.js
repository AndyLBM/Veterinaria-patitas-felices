const notes = { name: 'observaciones', label: 'Observaciones', type: 'textarea' };
export const CLINICAL_FIELDS = Object.freeze({
  atencion: [notes],
  triaje: [
    { name: 'peso', label: 'Peso', type: 'number', min: '0.01', max: '9999.99', step: '0.01' },
    { name: 'temperatura', label: 'Temperatura', type: 'number', min: '0.1', max: '999.9', step: '0.1' },
    { name: 'frecuencia_cardiaca', label: 'Frecuencia cardíaca', type: 'number', min: 1, max: 2147483647, step: 1 },
    { name: 'frecuencia_respiratoria', label: 'Frecuencia respiratoria', type: 'number', min: 1, max: 2147483647, step: 1 }, notes,
  ],
  consulta: [{ name: 'diagnostico', label: 'Diagnóstico', type: 'textarea', required: true, minLength: 1 }, { name: 'tratamiento', label: 'Tratamiento', type: 'textarea' }, notes],
  receta: [{ name: 'indicaciones', label: 'Indicaciones', type: 'textarea' }],
  detalle: [
    { name: 'medicamento', label: 'Medicamento', required: true, minLength: 1, maxLength: 150 },
    { name: 'dosis', label: 'Dosis', required: true, minLength: 1, maxLength: 100 },
    { name: 'frecuencia', label: 'Frecuencia', maxLength: 100 }, { name: 'duracion', label: 'Duración', maxLength: 100 },
    { name: 'indicaciones', label: 'Indicaciones', type: 'textarea' },
  ],
  vacuna: [
    { name: 'nombre_vacuna', label: 'Nombre de vacuna', required: true, minLength: 1, maxLength: 150 },
    { name: 'fecha_aplicacion', label: 'Fecha de aplicación', type: 'date', required: true },
    { name: 'proxima_dosis', label: 'Próxima dosis', type: 'date' }, notes,
  ],
});
export const CLINICAL_TITLES = Object.freeze({ atencion: 'Atención', triaje: 'Triaje', consulta: 'Consulta', receta: 'Receta', detalle: 'Medicamento', vacuna: 'Vacuna' });
export function clinicalPayload(kind, values) {
  if (!CLINICAL_FIELDS[kind]) throw new TypeError('Formulario clínico no válido.');
  return Object.fromEntries(CLINICAL_FIELDS[kind].map(f => {
    let value = String(values[f.name] ?? '').trim();
    if (!value && !f.required) value = null;
    if (value !== null && ['frecuencia_cardiaca', 'frecuencia_respiratoria'].includes(f.name)) value = Number(value);
    return [f.name, value];
  }));
}
export function agendaQuery(values) {
  const query = {};
  for (const key of ['fecha_desde', 'fecha_hasta', 'estado']) if (values[key]) query[key] = values[key];
  if (query.fecha_desde && query.fecha_hasta && query.fecha_desde > query.fecha_hasta) throw new TypeError('Revisa el rango de fechas.');
  return query;
}
export function agendaCounts(rows) { return { pendientes: rows.filter(r => ['PROGRAMADA', 'CONFIRMADA'].includes(r.estado)).length, enAtencion: rows.filter(r => r.estado === 'EN_ATENCION').length, atendidas: rows.filter(r => r.estado === 'ATENDIDA').length }; }
