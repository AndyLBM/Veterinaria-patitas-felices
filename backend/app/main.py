from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError

from backend.app.routers import (
    auth,
    atencion,
    consulta,
    detalle_receta,
    cita,
    cliente,
    especialidad,
    horario_veterinario,
    historial_clinico,
    mascota,
    receta,
    servicio,
    triaje,
    usuario,
    vacuna,
    veterinario,
)

app = FastAPI(
    title="API - Patitas Felices",
    description="API para la gestión del sistema veterinario Patitas Felices",
    version="1.0.0"
)

app.include_router(mascota.router)
app.include_router(cliente.router)
app.include_router(auth.router)
app.include_router(atencion.router)
app.include_router(triaje.router)
app.include_router(consulta.router)
app.include_router(receta.router)
app.include_router(detalle_receta.router)
app.include_router(cita.router)
app.include_router(especialidad.router)
app.include_router(servicio.router)
app.include_router(veterinario.router)
app.include_router(horario_veterinario.router)
app.include_router(usuario.router)
app.include_router(vacuna.router)
app.include_router(historial_clinico.router)


_MENSAJES_VALIDACION = {
    "missing": "Completa este campo.",
    "string_type": "Introduce un texto válido.",
    "string_too_short": "El texto es demasiado corto.",
    "string_too_long": "El texto supera la longitud permitida.",
    "int_type": "Introduce un número entero válido.",
    "int_parsing": "Introduce un número entero válido.",
    "float_type": "Introduce un número válido.",
    "float_parsing": "Introduce un número válido.",
    "decimal_type": "Introduce un número decimal válido.",
    "decimal_parsing": "Introduce un número decimal válido.",
    "greater_than": "El valor debe superar el mínimo permitido.",
    "greater_than_equal": "El valor no puede ser menor que el mínimo permitido.",
    "less_than": "El valor debe ser inferior al máximo permitido.",
    "less_than_equal": "El valor no puede superar el máximo permitido.",
    "literal_error": "Selecciona uno de los valores permitidos.",
    "date_type": "Introduce una fecha válida.",
    "date_parsing": "Introduce una fecha válida.",
    "date_from_datetime_parsing": "Introduce una fecha válida.",
    "datetime_type": "Introduce una fecha y hora válidas.",
    "datetime_parsing": "Introduce una fecha y hora válidas.",
    "datetime_from_date_parsing": "Introduce una fecha y hora válidas.",
    "json_invalid": "El cuerpo debe contener un JSON válido.",
    "value_error": "Revisa el valor de este campo.",
}


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, error: RequestValidationError):
    # No serializar input, body, ctx ni mensajes de validadores que podrían
    # incorporar contraseñas/tokens. Tampoco registrar la excepción o headers.
    detalles = []
    for detalle in error.errors():
        tipo = detalle.get("type")
        if tipo not in _MENSAJES_VALIDACION:
            tipo = "value_error"
        detalles.append({
            "loc": list(detalle.get("loc", ())),
            "type": tipo,
            "msg": _MENSAJES_VALIDACION[tipo],
        })
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        content={"detail": detalles})


@app.exception_handler(MySQLError)
async def manejar_error_mysql(request: Request, error: MySQLError):
    """Evita exponer detalles de MySQL a los consumidores de la API."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "El servicio de datos no está disponible"}
    )


@app.get("/")
def inicio():
    return {
        "mensaje": "API de Patitas Felices funcionando correctamente"
    }
