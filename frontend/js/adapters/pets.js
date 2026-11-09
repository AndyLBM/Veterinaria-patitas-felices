export const PET_SEX = Object.freeze({ NO_ESPECIFICADO: 'No especificado', MACHO: 'Macho', HEMBRA: 'Hembra' });
export const PET_FIELDS = Object.freeze([
  { name: 'nombre', label: 'Nombre', required: true, minLength: 2, maxLength: 80 },
  { name: 'especie', label: 'Especie', required: true, minLength: 2, maxLength: 50, hint: 'Escribe la especie de tu mascota.' },
  { name: 'raza', label: 'Raza (opcional)', maxLength: 80 },
  { name: 'sexo', label: 'Sexo', type: 'select', required: true, options: Object.entries(PET_SEX).map(([value, label]) => ({ value, label })) },
  { name: 'fecha_nacimiento', label: 'Fecha de nacimiento (opcional)', type: 'date' },
  { name: 'peso_referencial', label: 'Peso referencial (opcional)', type: 'number', min: '0.01', max: '9999.99', step: '0.01', hint: 'Mayor que cero, hasta 4 cifras enteras y 2 decimales.' },
]);
export function petPayload(values) {
  return Object.fromEntries(PET_FIELDS.map(f => {
    let value = String(values[f.name] ?? '').trim();
    if (f.name === 'sexo' && !value) value = 'NO_ESPECIFICADO';
    if (!value && !f.required) value = null;
    return [f.name, value];
  }));
}
export function petDate(value) {
  if (value == null || value === '') return 'Sin registrar';
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : 'Fecha no disponible';
}
