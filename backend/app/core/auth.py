from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.core.security import verificar_access_token

security = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
            headers={"WWW-Authenticate": "Bearer"}
        )

    datos = verificar_access_token(credentials.credentials)

    if datos is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "id_usuario": int(datos["sub"]),
        "id_rol": int(datos["id_rol"])
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