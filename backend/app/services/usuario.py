from backend.app.repositories import usuario as usuario_repository


def listar_usuarios():
    return usuario_repository.listar_usuarios()


def obtener_usuario(id_usuario: int):
    return usuario_repository.obtener_usuario_administracion(id_usuario)


def actualizar_estado_usuario(id_usuario: int, estado: str):
    usuario = obtener_usuario(id_usuario)
    if usuario is None:
        return None

    usuario_repository.actualizar_estado_usuario(id_usuario, estado)
    return {
        "mensaje": "Estado de la cuenta actualizado correctamente",
        "id_usuario": id_usuario,
        "estado": estado
    }
