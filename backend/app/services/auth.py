import bcrypt

from backend.app.repositories import auth as auth_repository
from backend.app.core.security import crear_access_token


def iniciar_sesion(datos):
    usuario = auth_repository.obtener_usuario_por_correo(datos.correo)

    if usuario is None:
        return None

    if usuario["estado"] != "ACTIVO":
        return None

    password_bytes = datos.password.encode("utf-8")

    if len(password_bytes) > 72:
        return None

    password_valida = bcrypt.checkpw(
        password_bytes,
        usuario["password_hash"].encode("utf-8")
    )

    if not password_valida:
        return None

    token = crear_access_token(
        id_usuario=usuario["id_usuario"],
        id_rol=usuario["id_rol"]
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"],
            "correo": usuario["correo"],
            "id_rol": usuario["id_rol"]
        }
    }