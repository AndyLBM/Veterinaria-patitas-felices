from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.core.security import verificar_access_token
from backend.app.repositories import auth as auth_repository
from backend.app.repositories import atencion as atencion_repository
from backend.app.repositories import cita as cita_repository
from backend.app.repositories import cliente as cliente_repository
from backend.app.repositories import mascota as mascota_repository
from backend.app.repositories import veterinario as veterinario_repository


ROL_ADMINISTRADOR = 1
ROL_VETERINARIO = 2
ROL_CLIENTE = 3

security = HTTPBearer(auto_error=False)


def _credenciales_invalidas(detalle: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detalle,
        headers={"WWW-Authenticate": "Bearer"}
    )


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Valida el JWT y vuelve a comprobar el estado y rol en MySQL.

    El token solamente identifica al usuario. La autorización usa los valores
    actuales de la base de datos, por lo que una desactivación o cambio de rol
    tiene efecto inmediato incluso si el token aún no expiró.
    """
    if credentials is None:
        _credenciales_invalidas("Se requiere autenticación")

    datos = verificar_access_token(credentials.credentials)

    if datos is None:
        _credenciales_invalidas("Token inválido o expirado")

    try:
        id_usuario = int(datos["sub"])
    except (KeyError, TypeError, ValueError):
        _credenciales_invalidas("Token inválido")

    usuario = auth_repository.obtener_usuario_por_id(id_usuario)

    if usuario is None or usuario["estado"] != "ACTIVO":
        _credenciales_invalidas("La cuenta no está activa")

    return {
        "id_usuario": usuario["id_usuario"],
        "id_rol": usuario["id_rol"]
    }


def requerir_roles(*roles_permitidos: int):
    def verificar_rol(usuario: dict = Depends(obtener_usuario_actual)):
        if usuario["id_rol"] not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operación"
            )

        return usuario

    return verificar_rol


def obtener_cliente_asociado(usuario: dict):
    """Obtiene la cuenta activa del cliente autenticado."""
    if usuario["id_rol"] != ROL_CLIENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación está disponible solo para clientes"
        )

    cliente = cliente_repository.obtener_cliente_por_usuario(
        usuario["id_usuario"]
    )

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No existe una cuenta de cliente activa asociada al usuario"
        )

    return cliente


def verificar_acceso_cliente(
    id_cliente: int,
    usuario: dict = Depends(obtener_usuario_actual)
):
    """Permite acceso al administrador o al propietario de la cuenta."""
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return usuario

    cliente = obtener_cliente_asociado(usuario)

    if cliente["id_cliente"] != id_cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos sobre este cliente"
        )

    return usuario


def verificar_acceso_mascota(
    id_mascota: int,
    usuario: dict = Depends(obtener_usuario_actual)
):
    """Permite acceso al administrador o al cliente propietario de la mascota."""
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return usuario

    cliente = obtener_cliente_asociado(usuario)
    mascota = mascota_repository.obtener_mascota(id_mascota)

    # La ruta conserva la respuesta 404 para mascotas inexistentes; para las
    # existentes, solo su propietario puede continuar.
    if mascota is not None and mascota["id_cliente"] != cliente["id_cliente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos sobre esta mascota"
        )

    return usuario


def verificar_acceso_cita(
    id_cita: int,
    usuario: dict = Depends(obtener_usuario_actual)
):
    """Permite acceso al administrador o al cliente propietario de la cita."""
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return usuario

    cliente = obtener_cliente_asociado(usuario)
    cita = cita_repository.obtener_cita(id_cita)

    # La ruta conserva la respuesta 404 para citas inexistentes; las citas
    # existentes solo pueden ser consultadas o gestionadas por su propietario.
    if cita is not None and cita["id_cliente"] != cliente["id_cliente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos sobre esta cita"
        )

    return usuario


def obtener_veterinario_asociado(usuario: dict = Depends(obtener_usuario_actual)):
    if usuario["id_rol"] != ROL_VETERINARIO:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Esta operación requiere un veterinario")
    veterinario = veterinario_repository.obtener_veterinario_por_usuario(usuario["id_usuario"])
    if veterinario is None or veterinario["estado"] != "ACTIVO":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No existe un perfil veterinario activo asociado")
    return veterinario


def verificar_lectura_cita(id_cita: int, usuario: dict = Depends(obtener_usuario_actual)):
    """Amplía solo la lectura; cancelar/reprogramar conservan sus permisos."""
    if usuario["id_rol"] == ROL_VETERINARIO:
        return verificar_acceso_cita_estado(id_cita, usuario)
    return verificar_acceso_cita(id_cita, usuario)


def verificar_acceso_cita_estado(id_cita: int, usuario: dict = Depends(obtener_usuario_actual)):
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return usuario
    veterinario = obtener_veterinario_asociado(usuario)
    cita = cita_repository.obtener_cita(id_cita)
    if cita is not None and cita["id_veterinario"] != veterinario["id_veterinario"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos sobre esta cita")
    return usuario


def verificar_acceso_atencion(id_atencion: int, usuario: dict = Depends(obtener_usuario_actual)):
    if usuario["id_rol"] == ROL_ADMINISTRADOR:
        return usuario
    veterinario = obtener_veterinario_asociado(usuario)
    atencion = atencion_repository.obtener_atencion(id_atencion)
    if atencion is not None and atencion["id_veterinario"] != veterinario["id_veterinario"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos sobre esta atención")
    return usuario
