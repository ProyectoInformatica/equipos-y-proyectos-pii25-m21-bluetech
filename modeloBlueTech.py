# Primera implementación del código del sprint 1:
# Incluye el inicio de sesión de usuarios/administrador
# Selección de rol. 
# 
# Segunda implementación del código del sprint 2:
# Incluye funciones para agregar y eliminar usuarios
# Incluye funciones para consultar y cambiar los parámetros de sanidad
# Incluye funciones para visualizar y cambiar el estado de ocupación de las salas
# Se emplea hash para las contraseñas 
#==============================================================================================
import json  # Se importa el módulo "json" para leer y escribir archivos en formato JSON.
import hashlib  # Se importa hashlib para poder calcular el hash (SHA-256) de las contraseñas.


# Clase que define los tipos de roles posibles para un usuario.
class Rol:
    ADMINISTRADOR = "administrador"
    TRABAJADOR = "trabajador"


# Clase que representa un usuario del sistema (como administrador o trabajador).
class Usuario:
    def __init__(self, id_usuario, nombre_usuario, contrasena_hash, rol):
        # Constructor que inicializa los atributos básicos del usuario.
        # En este caso, 'contrasena_hash' almacena el hash SHA-256 de la contraseña,
        # no la contraseña en texto plano.
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasena_hash = contrasena_hash
        self.rol = rol

    def verificar_contrasena(self, contrasena_ingresada):
        # Compara la contraseña ingresada con la almacenada y devuelve True si coinciden.
        # Ahora, en lugar de comparar texto plano, se calcula el hash de la contraseña
        # introducida por el usuario y se compara con el hash almacenado.
        hash_ingresado = hashlib.sha256(contrasena_ingresada.encode("utf-8")).hexdigest()
        return hash_ingresado == self.contrasena_hash

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
        # Históricamente se utilizaban dos archivos (uno para admins y otro para usuarios),
        # pero actualmente se está utilizando un único JSON (ruta_usuarios) que contiene
        # tanto administradores como trabajadores bajo la clave "usuarios".
        self.ruta_admins = ruta_admins        # Se mantiene por compatibilidad, aunque ya no se use.
        self.ruta_usuarios = ruta_usuarios    # Aquí se encuentra el JSON unificado con todos los usuarios.

        self.admins = []    # Lista donde se almacenan los administradores cargados.
        self.usuarios = []  # Lista donde se almacenan los usuarios cargados.
        self.cargar_datos() # Se llama automáticamente al método que carga los datos desde el archivo.

    def _obtener_nombre_login(self, entrada_json):
        # Método de apoyo que decide qué campo usar como nombre de usuario para el login.
        # El campo preferido es 'nombre_usuario'. Si no existe, se intenta utilizar 'nombre'.
        # Si ninguno está presente o es inválido, se devuelve None.

        # Intentar obtener el campo 'nombre_usuario'
        nombre_login = entrada_json.get("nombre_usuario")
        if isinstance(nombre_login, str) and len(nombre_login) > 0:
            return nombre_login

        # Si no existe 'nombre_usuario', intentar con 'nombre'
        nombre_login = entrada_json.get("nombre")
        if isinstance(nombre_login, str) and len(nombre_login) > 0:
            return nombre_login

        # Si no se encuentra un campo válido, se devuelve None
        return None

    def _obtener_contrasena_hash(self, entrada_json):
        # Método de apoyo que devuelve siempre un hash de la contraseña del usuario.
        # Este método permite trabajar con cualquiera de los siguientes escenarios:
        #
        # 1) El JSON ya contiene un hash (campos 'contrasena_hash' o 'contraseña_hash').
        #    En ese caso, se devuelve directamente el hash almacenado.
        #
        # 2) El JSON contiene la contraseña en texto plano (campos 'contraseña' o 'contrasena').
        #    En ese caso, aquí se calcula el hash SHA-256 y se devuelve.
        #    El JSON original NO se modifica; el hash se genera solo en memoria.
        #
        # 3) Si no existe ningún campo válido de contraseña, se devuelve None.

        # Intentar leer un hash ya existente en 'contrasena_hash'
        valor = entrada_json.get("contrasena_hash")
        if isinstance(valor, str) and len(valor) > 0:
            return valor

        # Intentar leer un hash ya existente en 'contraseña_hash'
        valor = entrada_json.get("contraseña_hash")
        if isinstance(valor, str) and len(valor) > 0:
            return valor

        # Si no hay hash, buscar contraseña en texto plano 'contraseña'
        plano = entrada_json.get("contraseña")
        if not isinstance(plano, str) or len(plano) == 0:
            # Si no está en 'contraseña', intentar 'contrasena'
            plano = entrada_json.get("contrasena")

        # Si se encuentra contraseña en texto plano, generar su hash SHA-256
        if isinstance(plano, str) and len(plano) > 0:
            return hashlib.sha256(plano.encode("utf-8")).hexdigest()

        # Si no hay ni hash ni contraseña en texto plano, no se puede autenticar al usuario
        return None

    def cargar_datos(self):
        # Carga los datos de los JSON y crea objetos Usuario para cada entrada.
        # En la versión actual, sólo se utiliza el archivo 'ruta_usuarios', que contiene
        # tanto administradores como trabajadores en una única lista llamada "usuarios".
        self.admins = []
        self.usuarios = []

        f2 = None
        try:
            # Se intenta abrir el archivo de usuarios (trabajadores y administradores).
            f2 = open(self.ruta_usuarios, "r", encoding="utf-8")
            data_users = json.load(f2)
            lista2 = data_users.get("usuarios", [])  # Se obtiene la lista de usuarios (de ambos roles).
            j = 0
            total2 = len(lista2)
            while j < total2:
                u = lista2[j]

                # Se determina el nombre de usuario que se utilizará para el login.
                nombre_login = self._obtener_nombre_login(u)

                # Se obtiene o genera el hash de la contraseña (según lo que haya en el JSON).
                contrasena_hash = self._obtener_contrasena_hash(u)

                # Se normaliza el rol leído del JSON (por ejemplo "administrador" o "trabajador").
                rol_texto = u.get("rol")
                rol_normalizado = None
                if isinstance(rol_texto, str):
                    rol_texto = rol_texto.strip().lower()
                    if rol_texto == Rol.ADMINISTRADOR:
                        rol_normalizado = Rol.ADMINISTRADOR
                    elif rol_texto == Rol.TRABAJADOR:
                        rol_normalizado = Rol.TRABAJADOR

                # Sólo creamos el usuario si tenemos nombre de login, hash de contraseña y rol válido.
                if nombre_login is not None and contrasena_hash is not None and rol_normalizado is not None:
                    nuevo = Usuario(
                        id_usuario=u.get("id_usuario"),
                        nombre_usuario=nombre_login,
                        contrasena_hash=contrasena_hash,
                        rol=rol_normalizado
                    )

                    # Se agrega el usuario a la lista correspondiente en función de su rol.
                    if rol_normalizado == Rol.ADMINISTRADOR:
                        self.admins.append(nuevo)
                    elif rol_normalizado == Rol.TRABAJADOR:
                        self.usuarios.append(nuevo)

                j = j + 1
        except FileNotFoundError:
            # Si no se encuentra el archivo, se muestra un mensaje.
            print("No se encontró el archivo de usuarios:", self.ruta_usuarios)
        if f2 is not None:
            f2.close()  # Se cierra el archivo si fue abierto correctamente.

    def verificar_login(self, nombre_usuario, contrasena, rol):
        # Método que verifica si un usuario (o administrador) existe y su contraseña es correcta.
        # Ahora utiliza el hash de la contraseña en lugar de texto plano.
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
            # Dentro de 'verificar_contrasena' se calcula el hash de la contraseña introducida.
            if u.nombre_usuario == nombre_usuario and u.verificar_contrasena(contrasena):
                encontrado = u  # Si coincide, se guarda el usuario encontrado.
            i = i + 1

        return encontrado  # Devuelve el objeto Usuario si fue encontrado, o None si no existe.
