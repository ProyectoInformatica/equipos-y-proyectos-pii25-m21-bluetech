from enum import Enum
import hashlib
import json
import os

class Rol(Enum):
    ADMINISTRADOR = "Administrador"
    TRABAJADOR = "Trabajador"

class Usuario:
    """Representa un usuario del sistema BlueTech."""

    def __init__(self, id_usuario, nombre, contrasena_hash, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.contrasena_hash = contrasena_hash
        self.rol = rol

    def verificar_contrasena(self, contrasena):
        """Compara la contraseña ingresada con el hash guardado."""
        hash_ingresado = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
        return hash_ingresado == self.contrasena_hash

    def es_administrador(self):
        return self.rol == Rol.ADMINISTRADOR

    def es_trabajador(self):
        return self.rol == Rol.TRABAJADOR

class RepositorioUsuarios:
    """Gestiona el almacenamiento y recuperación de usuarios en un archivo JSON."""

    def __init__(self, archivo="usuarios.json"):
        self.archivo = archivo
        self.usuarios = []
        self.cargar_datos()

    def cargar_datos(self):
        """Carga los usuarios desde el archivo JSON."""
        if os.path.exists(self.archivo):
            archivo_json = open(self.archivo, "r", encoding="utf-8")
            contenido = archivo_json.read()
            archivo_json.close()

            if len(contenido.strip()) > 0:
                datos = json.loads(contenido)
                self.usuarios = []
                for u in datos:
                    rol = Rol(u["rol"])
                    usuario = Usuario(u["id_usuario"], u["nombre"], u["contrasena_hash"], rol)
                    self.usuarios.append(usuario)
        else:
            self.usuarios = []

    def guardar_datos(self):
        """Guarda los usuarios en el archivo JSON."""
        lista_usuarios = []
        for u in self.usuarios:
            lista_usuarios.append({
                "id_usuario": u.id_usuario,
                "nombre": u.nombre,
                "contrasena_hash": u.contrasena_hash,
                "rol": u.rol.value
            })

        archivo_json = open(self.archivo, "w", encoding="utf-8")
        json.dump(lista_usuarios, archivo_json, ensure_ascii=False, indent=2)
        archivo_json.close()

    def buscar_por_id(self, id_usuario):
        """Busca un usuario por su ID."""
        encontrado = None
        for u in self.usuarios:
            if u.id_usuario == id_usuario:
                encontrado = u
        return encontrado

    def agregar_usuario(self, id_usuario, nombre, contrasena, rol):
        """Agrega un nuevo usuario al sistema si no existe."""
        usuario_existente = self.buscar_por_id(id_usuario)
        if usuario_existente is None:
            contrasena_hash = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
            nuevo_usuario = Usuario(id_usuario, nombre, contrasena_hash, rol)
            self.usuarios.append(nuevo_usuario)
            self.guardar_datos()
            return True
        else:
            return False

    def listar(self):
        return self.usuarios

def inicializar_usuarios_si_vacio(archivo="usuarios.json"):
    """Crea usuarios por defecto si el repositorio está vacío."""
    repositorio = RepositorioUsuarios(archivo)
    lista = repositorio.listar()

    if len(lista) == 0:
        repositorio.agregar_usuario("admin01", "Administrador", "admin123", Rol.ADMINISTRADOR)
        repositorio.agregar_usuario("trab01", "Trabajador", "trab123", Rol.TRABAJADOR)

def main():
    print("=== BlueTech · Sistema de Login ===")

    inicializar_usuarios_si_vacio()

    repo = RepositorioUsuarios()

    id_usuario = input("Ingrese su ID de usuario: ")
    contrasena = input("Ingrese su contraseña: ")

    usuario = repo.buscar_por_id(id_usuario)

    if usuario is not None:
        if usuario.verificar_contrasena(contrasena):
            print("\nAcceso concedido.")
            print("Bienvenido/a:", usuario.nombre)
            print("Rol:", usuario.rol.value)
        else:
            print("\nContraseña incorrecta.")
    else:
        print("\nUsuario no encontrado.")


