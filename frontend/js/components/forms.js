export function field({ id, name = id, label, hint = '', required = false, type = 'text', minLength, maxLength, autocomplete, min, max, step, options = [] }) {
  const wrapper = document.createElement('div');
  wrapper.className = 'field';
  const caption = document.createElement('label');
  caption.htmlFor = id;
  caption.textContent = label + (required ? ' (obligatorio)' : '');
  const input = document.createElement(type === 'select' ? 'select' : type === 'textarea' ? 'textarea' : 'input');
  input.id = id;
  input.name = name;
  if (input.tagName === 'INPUT') input.type = type;
  if (type === 'textarea') input.rows = 3;
  if (type === 'select') for (const item of options) {
    const option = document.createElement('option'); option.value = item.value; option.textContent = item.label; input.append(option);
  }
  input.required = required;
  if (minLength !== undefined) input.minLength = minLength;
  if (maxLength !== undefined) input.maxLength = maxLength;
  if (autocomplete) input.autocomplete = autocomplete;
  for (const [key, value] of Object.entries({ min, max, step })) if (value !== undefined) input.setAttribute(key, value);
  input.setAttribute('aria-describedby', `${id}-hint ${id}-error`);
  const help = document.createElement('small');
  help.id = `${id}-hint`;
  help.textContent = hint;
  const error = document.createElement('small');
  error.className = 'field-error';
  error.id = `${id}-error`;
  error.setAttribute('aria-live', 'polite');
  wrapper.append(caption, input, help, error);
  return wrapper;
}
export function setFieldError(input, message = '') {
  input.setAttribute('aria-invalid', String(Boolean(message)));
  const target = input.ownerDocument.getElementById(`${input.id}-error`);
  if (target) target.textContent = message;
}
export function validateForm(form) {
  let firstInvalid;
  for (const input of form.querySelectorAll('input, select, textarea')) {
    const length = [...input.value].length;
    let message = input.validity.valueMissing ? 'Completa este campo.' : input.validity.typeMismatch ? 'Introduce un correo electrónico válido.' : input.validity.valid ? '' : 'Revisa el valor de este campo.';
    if (!message && input.value && input.minLength > 0 && length < input.minLength) message = `Introduce al menos ${input.minLength} caracteres.`;
    if (!message && input.maxLength >= 0 && length > input.maxLength) message = `No superes los ${input.maxLength} caracteres.`;
    if (!message && input.type === 'password' && new TextEncoder().encode(input.value).length > 72) message = 'La contraseña no puede superar los 72 bytes en UTF-8.';
    setFieldError(input, message);
    if (message && !firstInvalid) firstInvalid = input;
  }
  firstInvalid?.focus();
  return !firstInvalid;
}
