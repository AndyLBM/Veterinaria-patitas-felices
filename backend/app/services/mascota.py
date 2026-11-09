
from mysql.connector import Error

from backend.app.repositories import mascota as mascota_repository


# ==========================================
# 1. LISTAR MASCOTAS
# ==========================================

def listar_mascotas():

    try:
        return mascota_repository.listar_mascotas()

    except Error:
        raise


def listar_mascotas_por_cliente(id_cliente: int):

    try:
        return mascota_repository.listar_mascotas_por_cliente(id_cliente)

    except Error:
        raise


# ==========================================
# 2. OBTENER MASCOTA POR ID
# ==========================================

def obtener_mascota(id_mascota: int):

    try:
        mascota = mascota_repository.obtener_mascota(id_mascota)

        if mascota is None:
            return None

        return mascota

    except Error:
        raise


# ==========================================
# 3. REGISTRAR MASCOTA
# ==========================================

def registrar_mascota(datos):

    try:
        # Verificar que el cliente exista
        cliente_existe = mascota_repository.existe_cliente(
            datos.id_cliente
        )

        if not cliente_existe:
            raise ValueError("El cliente indicado no existe")

        # Registrar la mascota
        id_mascota = mascota_repository.registrar_mascota(datos)

        return {
            "id_mascota": id_mascota,
            "mensaje": "Mascota registrada correctamente"
        }

    except Error:
        raise


# ==========================================
# 4. ACTUALIZAR MASCOTA
# ==========================================

def actualizar_mascota(id_mascota, datos):

    # Verificar si la mascota existe y está activa
    mascota = mascota_repository.obtener_mascota(id_mascota)

    if mascota is None:
        return None

    # Obtener únicamente los campos enviados
    campos = datos.model_dump(exclude_unset=True)

    # Si no se envió ningún campo, no hay actualización
    if not campos:
        raise ValueError("Debe enviar al menos un campo para actualizar")

    # Validar el cliente solamente si se envió id_cliente
    if "id_cliente" in campos:
        cliente_existe = mascota_repository.existe_cliente(
            campos["id_cliente"]
        )

        if not cliente_existe:
            raise ValueError("El cliente indicado no existe")

    # Ejecutar la actualización
    return mascota_repository.actualizar_mascota(
        id_mascota,
        datos
    )


# ==========================================
# 5. DESACTIVAR MASCOTA
# ==========================================

def desactivar_mascota(id_mascota: int):

    try:
        # Comprobar que la mascota exista
        mascota = mascota_repository.obtener_mascota(id_mascota)

        if mascota is None:
            return False

        return mascota_repository.desactivar_mascota(id_mascota)

    except Error:
        raise
