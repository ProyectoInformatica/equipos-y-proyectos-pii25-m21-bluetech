import json

class Rol:
    ADMINISTRADOR = "administrador"
    TRABAJADOR = "trabajador"


class Usuario:
    def __init__(self, id_usuario, nombre_usuario, contrasena, rol):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.rol = rol

    def verificar_contrasena(self, contrasena_ingresada):
        return contrasena_ingresada == self.contrasena

    def es_administrador(self):
        return self.rol == Rol.ADMINISTRADOR

    def es_trabajador(self):
        return self.rol == Rol.TRABAJADOR


class RepositorioCredenciales:
    def __init__(self, ruta_admins="admins.json", ruta_usuarios="usuarios.json"):
        self.ruta_admins = ruta_admins
        self.ruta_usuarios = ruta_usuarios
        self.admins = []
        self.usuarios = []
        self.cargar_datos()

    def cargar_datos(self):
        self.admins = []
        self.usuarios = []

        f = None
        try:
            f = open(self.ruta_admins, "r", encoding="utf-8")
            data_admins = json.load(f)
            lista = data_admins.get("admins", [])
            i = 0
            total = len(lista)
            while i < total:
                a = lista[i]
                nuevo = Usuario(
                    id_usuario=a.get("id_admin"),
                    nombre_usuario=a.get("nombre_usuario"),
                    contrasena=a.get("contraseña") or a.get("contraseña_hash"),
                    rol=Rol.ADMINISTRADOR
                )
                self.admins.append(nuevo)
                i = i + 1
        except FileNotFoundError:
            print("No se encontró el archivo de administradores:", self.ruta_admins)
        if f is not None:
            f.close()

        f2 = None
        try:
            f2 = open(self.ruta_usuarios, "r", encoding="utf-8")
            data_users = json.load(f2)
            lista2 = data_users.get("usuarios", [])
            j = 0
            total2 = len(lista2)
            while j < total2:
                u = lista2[j]
                nuevo = Usuario(
                    id_usuario=u.get("id_usuario"),
                    nombre_usuario=u.get("nombre"),
                    contrasena=u.get("contraseña") or u.get("contraseña_hash"),
                    rol=Rol.TRABAJADOR
                )
                self.usuarios.append(nuevo)
                j = j + 1
        except FileNotFoundError:
            print("No se encontró el archivo de usuarios:", self.ruta_usuarios)
        if f2 is not None:
            f2.close()

    def verificar_login(self, nombre_usuario, contrasena, rol):
        if rol == Rol.ADMINISTRADOR:
            lista = self.admins
        else:
            lista = self.usuarios

        encontrado = None
        i = 0
        total = len(lista)
        while i < total and encontrado is None:
            u = lista[i]
            if u.nombre_usuario == nombre_usuario and u.verificar_contrasena(contrasena):
                encontrado = u
            i = i + 1

        return encontrado
