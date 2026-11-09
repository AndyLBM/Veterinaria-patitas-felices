import { auth } from '../api/auth.js';
import { field, validateForm, setFieldError } from '../components/forms.js';
import { button, withBusy } from '../components/buttons.js';
import { errorMessage } from '../core/errors.js';

export function mountAuth(kind, { host, signal }) {
  const registering = kind === 'register';
  const form = host.querySelector('[data-auth-form]');
  const fields = form.querySelector('[data-auth-fields]');
  const prefix = registering ? 'register' : 'login';
  const add = options => fields.append(field({ id: `${prefix}-${options.name}`, ...options }));
  if (registering) {
    add({ name: 'nombre', label: 'Nombre', required: true, minLength: 2, maxLength: 80, autocomplete: 'given-name' });
    add({ name: 'apellido', label: 'Apellido', required: true, minLength: 2, maxLength: 80, autocomplete: 'family-name' });
  }
  add({ name: 'correo', label: 'Correo electrónico', required: true, type: 'email', minLength: 5, maxLength: 150, autocomplete: registering ? 'email' : 'username' });
  add({ name: 'password', label: 'Contraseña', required: true, type: 'password', minLength: registering ? 8 : 1, maxLength: 72, autocomplete: registering ? 'new-password' : 'current-password', hint: registering ? 'De 8 a 72 caracteres; máximo 72 bytes en UTF-8.' : 'La contraseña de tu cuenta de Patitas Felices.' });
  if (registering) add({ name: 'telefono', label: 'Teléfono (opcional)', type: 'tel', maxLength: 20, autocomplete: 'tel' });
  const submit = button(registering ? 'Crear mi cuenta' : 'Iniciar sesión', { type: 'submit', iconName: 'arrow' });
  form.append(submit);
  const alert = host.querySelector('[data-auth-error]');
  const cleanup = () => { form.reset(); alert.textContent = ''; };
  signal.addEventListener('abort', cleanup, { once: true });
  form.addEventListener('input', event => { if (event.target.matches('input')) setFieldError(event.target); }, { signal });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (submit.disabled || signal.aborted) return;
    for (const name of ['nombre', 'apellido', 'correo', 'telefono']) if (form.elements[name]) form.elements[name].value = form.elements[name].value.trim();
    alert.hidden = true; alert.textContent = '';
    if (!validateForm(form)) return;
    await withBusy(submit, async () => {
      const data = Object.fromEntries(new FormData(form));
      form.setAttribute('aria-busy', 'true');
      try {
        if (registering) {
          await auth.register(data, { signal });
          if (signal.aborted) return;
          form.reset(); form.hidden = true;
          const confirmation = host.querySelector('[data-registration-success]');
          confirmation.hidden = false;
          const title = confirmation.querySelector('h2'); title.tabIndex = -1; title.focus();
        } else {
          const destination = await auth.login(data, { signal });
          if (!signal.aborted) window.location.hash = destination;
        }
      } catch (error) {
        if (signal.aborted || error.code === 'ABORTED') return;
        alert.textContent = errorMessage(error); alert.hidden = false;
        for (const detail of error.fields || []) {
          const input = form.elements[detail.field];
          if (input instanceof HTMLInputElement) setFieldError(input, detail.message);
        }
        if (registering && error.status === 409) setFieldError(form.elements.correo, 'Este correo ya está registrado.');
        alert.focus();
      } finally {
        data.password = '';
        form.elements.password.value = '';
        form.removeAttribute('aria-busy');
      }
    });
  }, { signal });
  return cleanup;
}
