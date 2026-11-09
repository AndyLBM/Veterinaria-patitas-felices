
import bcrypt

from backend.app.repositories import cliente as cliente_repository


def registrar_cliente(datos):

    # 1. Convertir la contraseña a bytes
    password_bytes = datos.password.encode("utf-8")

    # 2. Verificar el límite de bcrypt
    if len(password_bytes) > 72:
        raise ValueError(
            "La contraseña no puede superar los 72 bytes"
        )

    # 3. Generar una sal aleatoria
    salt = bcrypt.gensalt()

    # 4. Generar el hash de la contraseña
    password_hash = bcrypt.hashpw(
        password_bytes,
        salt
    ).decode("utf-8")

    # 5. Registrar el cliente en la base de datos
    resultado = cliente_repository.registrar_cliente(
        datos,
        password_hash
    )

    return {
        "mensaje": "Cliente registrado correctamente",
        "id_cliente": resultado["id_cliente"]
    }

def listar_clientes():

    clientes = cliente_repository.listar_clientes()

    return clientes

def obtener_cliente(id_cliente):

    cliente = cliente_repository.obtener_cliente(id_cliente)

    return cliente

def actualizar_cliente(id_cliente, datos):

    # 1. Verificar que el cliente exista y esté activo
    cliente = cliente_repository.obtener_cliente(id_cliente)

    if cliente is None:
        return None

    # 2. Obtener únicamente los campos enviados
    campos = datos.model_dump(exclude_unset=True)

    if not campos:
        raise ValueError(
            "Debe proporcionar al menos un campo para actualizar"
        )

    # 3. Actualizar los datos mediante el Repository
    resultado = cliente_repository.actualizar_cliente(
        id_cliente,
        datos
    )

    return {
        "mensaje": "Cliente actualizado correctamente",
        "id_cliente": id_cliente
    } if resultado else None

def desactivar_cliente(id_cliente):

    # 1. Verificar que el cliente exista y esté activo
    cliente = cliente_repository.obtener_cliente(id_cliente)

    if cliente is None:
        return None

    # 2. Desactivar el cliente mediante el Repository
    resultado = cliente_repository.desactivar_cliente(id_cliente)

    if not resultado:
        return None

    return {
        "mensaje": "Cliente desactivado correctamente",
        "id_cliente": id_cliente
    }