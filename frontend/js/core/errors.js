const MESSAGES = {
  400: 'Revisa los datos o el estado de la operación.',
  401: 'Tu sesión no está disponible o ha vencido. Inicia sesión nuevamente.',
  403: 'No tienes permisos para realizar esta operación.',
  404: 'No se encontró el recurso solicitado.',
  409: 'La información entra en conflicto con un registro existente.',
  422: 'Hay campos que necesitan revisión.',
  503: 'El servicio de datos no está disponible. Inténtalo más tarde.',
};

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'HTTP_ERROR', fields = [], cause } = {}) {
    super(message, { cause });
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

export function responseError(status, body) {
  const fields = Array.isArray(body?.detail) ? body.detail.map(error => ({
    field: (error.loc || []).filter(part => !['body', 'query', 'path'].includes(part)).join('.'),
    message: typeof error.msg === 'string' ? error.msg : 'Valor no válido.',
  })) : [];
  // No se muestran HTML de Apache, trazas ni respuestas internas de errores 5xx.
  const detail = status < 500 && typeof body?.detail === 'string' ? body.detail : null;
  return new ApiError(detail || MESSAGES[status] || 'No se pudo completar la solicitud.', { status, fields });
}

export function errorMessage(error) {
  return error instanceof ApiError ? error.message : 'Ocurrió un problema inesperado. Inténtalo nuevamente.';
}
