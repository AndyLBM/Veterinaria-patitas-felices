import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("No se ha configurado JWT_SECRET_KEY en el archivo .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def crear_access_token(id_usuario: int, id_rol: int):
    fecha_expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datos_token = {
        "sub": str(id_usuario),
        "id_rol": id_rol,
        "exp": fecha_expiracion
    }

    token = jwt.encode(
        datos_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verificar_access_token(token: str):
    try:
        datos = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return datos

    except jwt.InvalidTokenError:
        return None