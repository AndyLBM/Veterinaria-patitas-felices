from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.core.dependencies import (
    ROL_ADMINISTRADOR,
    ROL_CLIENTE,
    obtener_cliente_asociado,
    obtener_usuario_actual,
    obtener_veterinario_asociado,
    requerir_roles,
    verificar_acceso_cita,
    verificar_acceso_cita_estado,
    verificar_lectura_cita,
)
from backend.app.schemas.cita import (
    CitaCreate,
    CitaAgendaResponse,
    CitaEstadoUpdate,
    CitaReprogramacion,
    EstadoCita,
)
from backend.app.services import cita as cita_service
from backend.app.services import atencion as atencion_service


router = APIRouter(prefix="/citas", tags=["Citas y disponibilidad"])


def _obtener_cliente_permitido(usuario: dict) -> int | None:
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return None

    if usuario["id_rol"] == ROL_CLIENTE:
        return obtener_cliente_asociado(usuario)["id_cliente"]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para gestionar citas"
    )


def _manejar_error_operacion(error: Exception):
    if isinstance(error, PermissionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error)
        )
    if isinstance(error, LookupError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    if isinstance(error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    raise error


@router.get("/servicios-disponibles")
def listar_servicios_disponibles(
    usuario: dict = Depends(obtener_usuario_actual)
):
    _obtener_cliente_permitido(usuario)
    return cita_service.listar_servicios_disponibles()


@router.get("/veterinarios-disponibles")
def listar_veterinarios_disponibles(
    id_servicio: int = Query(gt=0),
    fecha: date = Query(),
    usuario: dict = Depends(obtener_usuario_actual)
):
    _obtener_cliente_permitido(usuario)
    try:
        return cita_service.listar_veterinarios_disponibles(id_servicio, fecha)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/disponibilidad")
def consultar_disponibilidad(
    id_veterinario: int = Query(gt=0),
    id_servicio: int = Query(gt=0),
    fecha: date = Query(),
    usuario: dict = Depends(obtener_usuario_actual)
):
    _obtener_cliente_permitido(usuario)
    try:
        return cita_service.consultar_disponibilidad(
            id_veterinario,
            id_servicio,
            fecha
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/mis-citas")
def listar_mis_citas(
    usuario: dict = Depends(obtener_usuario_actual)
):
    cliente = obtener_cliente_asociado(usuario)
    return cita_service.listar_mis_citas(cliente["id_cliente"])


@router.get("/mi-agenda", response_model=list[CitaAgendaResponse])
def listar_mi_agenda(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    estado: EstadoCita | None = None,
    veterinario: dict = Depends(obtener_veterinario_asociado)
):
    try:
        return cita_service.listar_mi_agenda(
            veterinario["id_veterinario"], fecha_desde, fecha_hasta, estado
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_cita(
    datos: CitaCreate,
    usuario: dict = Depends(obtener_usuario_actual)
):
    try:
        id_cliente_permitido = _obtener_cliente_permitido(usuario)
        return cita_service.registrar_cita(datos, id_cliente_permitido)
    except (PermissionError, LookupError, ValueError) as error:
        _manejar_error_operacion(error)


@router.get("/")
def listar_citas_administracion(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    estado: EstadoCita | None = None,
    id_veterinario: int | None = Query(default=None, gt=0),
    id_cliente: int | None = Query(default=None, gt=0),
    usuario: dict = Depends(requerir_roles(ROL_ADMINISTRADOR))
):
    try:
        return cita_service.listar_citas_administracion(
            fecha_desde,
            fecha_hasta,
            estado,
            id_veterinario,
            id_cliente
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get("/{id_cita}")
def obtener_cita(
    id_cita: int,
    usuario: dict = Depends(verificar_lectura_cita)
):
    cita = cita_service.obtener_cita(id_cita)
    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    return cita


@router.get("/{id_cita}/atencion")
def obtener_atencion_por_cita(
    id_cita: int,
    usuario: dict = Depends(verificar_acceso_cita_estado)
):
    atencion = atencion_service.obtener_atencion_por_cita(id_cita)
    if atencion is None:
        raise HTTPException(status_code=404, detail="No existe una atención para esta cita")
    return atencion


@router.get("/{id_cita}/disponibilidad-reprogramacion")
def consultar_disponibilidad_reprogramacion(
    id_cita: int,
    id_veterinario: int = Query(gt=0),
    fecha: date = Query(),
    usuario: dict = Depends(verificar_acceso_cita)
):
    try:
        return cita_service.consultar_disponibilidad_reprogramacion(
            id_cita, id_veterinario, fecha, _obtener_cliente_permitido(usuario)
        )
    except (PermissionError, LookupError, ValueError) as error:
        _manejar_error_operacion(error)


@router.patch("/{id_cita}/reprogramacion")
def reprogramar_cita(
    id_cita: int,
    datos: CitaReprogramacion,
    usuario: dict = Depends(verificar_acceso_cita)
):
    try:
        id_cliente_permitido = _obtener_cliente_permitido(usuario)
        return cita_service.reprogramar_cita(
            id_cita,
            datos,
            id_cliente_permitido
        )
    except (PermissionError, LookupError, ValueError) as error:
        _manejar_error_operacion(error)


@router.patch("/{id_cita}/cancelacion")
def cancelar_cita(
    id_cita: int,
    usuario: dict = Depends(verificar_acceso_cita)
):
    try:
        id_cliente_permitido = _obtener_cliente_permitido(usuario)
        return cita_service.cancelar_cita(id_cita, id_cliente_permitido)
    except (PermissionError, LookupError, ValueError) as error:
        _manejar_error_operacion(error)


@router.patch("/{id_cita}/estado")
def actualizar_estado_cita(
    id_cita: int,
    datos: CitaEstadoUpdate,
    usuario: dict = Depends(verificar_acceso_cita_estado)
):
    try:
        resultado = cita_service.actualizar_estado_cita(id_cita, datos.estado)
        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada"
            )

        return resultado
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
