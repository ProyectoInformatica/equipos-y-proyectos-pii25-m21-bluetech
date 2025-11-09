#Primera implementación del código del sprint 1:
# Incluye el inicio de sesión de usuarios/administrador
# Selección de rol.  
#==============================================================================================
import json  # Se importa el módulo "json" para leer y escribir archivos en formato JSON.

# Clase que define los tipos de roles posibles para un usuario.
class Rol:
    ADMINISTRADOR = "administrador"
    TRABAJADOR = "trabajador"


# Clase que representa un usuario del sistema (como administrador o trabajador).
class Usuario:
    def __init__(self, id_usuario, nombre_usuario, contrasena, rol):
        # Constructor que inicializa los atributos básicos del usuario.
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.rol = rol

    def verificar_contrasena(self, contrasena_ingresada):
        # Compara la contraseña ingresada con la almacenada y devuelve True si coinciden.
        return contrasena_ingresada == self.contrasena

    def es_administrador(self):
        # Devuelve True si el usuario tiene rol de administrador.
        return self.rol == Rol.ADMINISTRADOR

    def es_trabajador(self):
        # Devuelve True si el usuario tiene rol de trabajador.
        return self.rol == Rol.TRABAJADOR


# Clase encargada de manejar las credenciales de los JSON.
class RepositorioCredenciales:
    def __init__(self, ruta_admins="admins.json", ruta_usuarios="usuarios.json"):
        # Constructor que define las rutas de los archivos y carga los datos.
        self.ruta_admins = ruta_admins
        self.ruta_usuarios = ruta_usuarios
        self.admins = []    # Lista donde se almacenan los administradores cargados.
        self.usuarios = []  # Lista donde se almacenan los usuarios cargados.
        self.cargar_datos() # Se llama automáticamente al método que carga los datos desde los archivos.

    def cargar_datos(self):
        # Carga los datos de los JSON y crea objetos Usuario para cada entrada.
        self.admins = []
        self.usuarios = []

        f = None
        try:
            # Se intenta abrir el archivo de administradores.
            f = open(self.ruta_admins, "r", encoding="utf-8")
            data_admins = json.load(f)  # Se cargan los datos del archivo JSON.
            lista = data_admins.get("admins", [])  # Se obtiene la lista de administradores.
            i = 0
            total = len(lista)
            while i < total:
                a = lista[i]
                # Se crea un nuevo objeto Usuario con los datos del archivo.
                nuevo = Usuario(
                    id_usuario=a.get("id_admin"),
                    nombre_usuario=a.get("nombre_usuario"),
                    contrasena=a.get("contraseña") or a.get("contraseña_hash"),  # Usa 'contraseña_hash' si no existe 'contraseña'.
                    rol=Rol.ADMINISTRADOR
                )
                self.admins.append(nuevo)  # Se agrega a la lista de administradores.
                i = i + 1
        except FileNotFoundError:
            # Si no se encuentra el archivo, se muestra un mensaje.
            print("No se encontró el archivo de administradores:", self.ruta_admins)
        if f is not None:
            f.close()  # Se cierra el archivo si fue abierto correctamente.

        f2 = None
        try:
            # Se intenta abrir el archivo de usuarios (trabajadores).
            f2 = open(self.ruta_usuarios, "r", encoding="utf-8")
            data_users = json.load(f2)
            lista2 = data_users.get("usuarios", [])  # Se obtiene la lista de usuarios.
            j = 0
            total2 = len(lista2)
            while j < total2:
                u = lista2[j]
                # Se crea un nuevo objeto Usuario con los datos del archivo.
                nuevo = Usuario(
                    id_usuario=u.get("id_usuario"),
                    nombre_usuario=u.get("nombre"),
                    contrasena=u.get("contraseña") or u.get("contraseña_hash"),
                    rol=Rol.TRABAJADOR
                )
                self.usuarios.append(nuevo)  # Se agrega a la lista de usuarios.
                j = j + 1
        except FileNotFoundError:
            # Si no se encuentra el archivo, se muestra un mensaje.
            print("No se encontró el archivo de usuarios:", self.ruta_usuarios)
        if f2 is not None:
            f2.close()  # Se cierra el archivo si fue abierto correctamente.

    def verificar_login(self, nombre_usuario, contrasena, rol):
        # Método que verifica si un usuario (o administrador) existe y su contraseña es correcta.
        if rol == Rol.ADMINISTRADOR:
            lista = self.admins
        else:
            lista = self.usuarios

        encontrado = None
        i = 0
        total = len(lista)
        # Se recorre la lista del tipo de usuario correspondiente.
        while i < total and encontrado is None:
            u = lista[i]
            # Se compara el nombre y la contraseña.
            if u.nombre_usuario == nombre_usuario and u.verificar_contrasena(contrasena):
                encontrado = u  # Si coincide, se guarda el usuario encontrado.
            i = i + 1

        return encontrado  # Devuelve el objeto Usuario si fue encontrado, o None si no existe.
