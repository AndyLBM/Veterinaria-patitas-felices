"""Fechas de negocio: MySQL conserva la hora civil de America/Lima."""
from datetime import datetime
from zoneinfo import ZoneInfo


ZONA_NEGOCIO = ZoneInfo("America/Lima")


def fecha_local_lima(valor: datetime) -> datetime:
    """Sin offset significa Lima; con offset se conserva el instante recibido."""
    if valor.tzinfo is not None:
        return valor.astimezone(ZONA_NEGOCIO).replace(tzinfo=None)
    return valor


def ahora_lima() -> datetime:
    return datetime.now(ZONA_NEGOCIO).replace(tzinfo=None)


def validar_inicio_no_pasado(valor: datetime) -> None:
    """Comprobar al escribir; no aplica a lecturas ni a citas históricas."""
    # cita usa DATETIME(0): comprobar el segundo que realmente se conservará,
    # no una fracción que al persistirse podría convertirse en una fecha pasada.
    if fecha_local_lima(valor).replace(microsecond=0) < ahora_lima():
        raise ValueError(
            "La fecha y hora de inicio no pueden estar en el pasado (America/Lima)"
        )
