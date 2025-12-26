from model.modeloBlueTech import RepositorioCredenciales

# Repositorio único para toda la aplicación
repo = RepositorioCredenciales(ruta_usuarios="data/usuarios.json")

def verificar_usuario(nombre_usuario, contrasena, rol):
    return repo.verificar_login(nombre_usuario, contrasena, rol)

def agregar_trabajador(nombre, apellidos, nombre_usuario, contrasena):
    return repo.agregar_trabajador(nombre, apellidos, nombre_usuario, contrasena)

def eliminar_usuario(id_usuario):
    return repo.eliminar_usuario_por_id(id_usuario)

def guardar_cambios():
    if hasattr(repo, "guardar_cambios"):
        repo.guardar_cambios()