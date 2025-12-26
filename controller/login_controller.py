from model.modeloBlueTech import Rol

# Opcional: solo si quieres mantener funciones de autenticar con lógica extendida
def autenticar_usuario(repo, nombre, contrasena):
    if not nombre or not contrasena:
        return None
    return repo.verificar_login(nombre, contrasena)
