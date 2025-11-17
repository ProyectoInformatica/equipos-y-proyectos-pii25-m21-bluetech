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

import json      # Se importa el módulo "json" para leer y escribir archivos en formato JSON.
import hashlib   # Se importa hashlib para poder calcular el hash (SHA-256) de las contraseñas.


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
        # Se calcula el hash de la contraseña introducida y se compara con el hash guardado.
        hash_ingresado = hashlib.sha256(contrasena_ingresada.encode("utf-8")).hexdigest()
        return hash_ingresado == self.contrasena_hash

    def es_administrador(self):
        # Devuelve True si el usuario tiene rol de administrador.
        return self.rol == Rol.ADMINISTRADOR

    def es_trabajador(self):
        # Devuelve True si el usuario tiene rol de trabajador.
        return self.rol == Rol.TRABAJADOR


# Clase encargada de manejar las credenciales del JSON unificado de usuarios.
class RepositorioCredenciales:
    def __init__(self, ruta_usuarios="usuarios.json"):
        # Constructor que define la ruta del archivo y carga los datos.
        # Actualmente se utiliza un único JSON (ruta_usuarios) que contiene
        # tanto administradores como trabajadores bajo la clave "usuarios".
        self.ruta_usuarios = ruta_usuarios    # Aquí se encuentra el JSON con todos los usuarios.

        # Lista donde se almacenan todos los usuarios cargados (admins y trabajadores).
        self.usuarios = []

        # Se llama automáticamente al método que carga los datos desde el archivo.
        self.cargar_datos()

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
        # Carga los datos del JSON y crea objetos Usuario para cada entrada.
        # En la versión actual, se utiliza el archivo 'ruta_usuarios', que contiene
        # administradores y trabajadores en una única lista llamada "usuarios".
        self.usuarios = []

        f2 = None
        try:
            # Se intenta abrir el archivo de usuarios (trabajadores y administradores).
            f2 = open(self.ruta_usuarios, "r", encoding="utf-8")
            data_users = json.load(f2)

            # Se obtiene la lista de usuarios (de ambos roles).
            lista = data_users.get("usuarios", [])

            j = 0
            total = len(lista)
            while j < total:
                u = lista[j]

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

                    # Se agrega el usuario a la lista general de usuarios (admins y trabajadores).
                    self.usuarios.append(nuevo)

                j = j + 1

        except FileNotFoundError:
            # Si no se encuentra el archivo, se muestra un mensaje.
            print("No se encontró el archivo de usuarios:", self.ruta_usuarios)

        if f2 is not None:
            f2.close()  # Se cierra el archivo si fue abierto correctamente.

    def verificar_login(self, nombre_usuario, contrasena, rol):
        # Método que verifica si un usuario existe y su contraseña es correcta.
        # Ahora utiliza el hash de la contraseña en lugar de texto plano.
        # Se comprueba también que el rol del usuario coincida con el rol seleccionado.
        encontrado = None
        i = 0
        total = len(self.usuarios)

        # Se recorre la lista completa de usuarios (administradores y trabajadores).
        while i < total and encontrado is None:
            u = self.usuarios[i]

            if (
                u.nombre_usuario == nombre_usuario
                and u.rol == rol
                and u.verificar_contrasena(contrasena)
            ):
                # Si coincide el login, el rol y la contraseña, se guarda el usuario.
                encontrado = u

            i = i + 1

        # Devuelve el objeto Usuario si fue encontrado, o None si no existe o los datos no coinciden.
        return encontrado

    def eliminar_usuario_por_id(self, id_usuario):
        # Elimina un usuario del sistema a partir de su ID.
        # La eliminación se hace sobre el archivo JSON de usuarios (self.ruta_usuarios)
        # y después se recarga la información en memoria llamando a cargar_datos().

        # Primero intentamos leer el archivo JSON de usuarios.
        datos = None
        f = None

        try:
            f = open(self.ruta_usuarios, "r", encoding="utf-8")
            datos = json.load(f)
        except FileNotFoundError:
            # Si no existe el archivo, no se puede realizar la eliminación.
            print("\nNo se encontró el archivo de usuarios:", self.ruta_usuarios)
            return

        if f is not None:
            f.close()

        # Obtenemos la lista de usuarios del JSON.
        lista = datos.get("usuarios", [])
        if not isinstance(lista, list):
            print("\nLa estructura del archivo de usuarios no es válida.")
            return

        # Buscamos el índice del usuario cuyo id coincida con el indicado.
        # Detenemos la búsqueda cuando 'indice_encontrado' deja de ser -1.
        indice_encontrado = -1
        i = 0
        total = len(lista)
        id_busqueda = id_usuario

        # Si id_usuario viene como texto, intentamos convertirlo a entero.
        if isinstance(id_busqueda, str) and id_busqueda.isdigit():
            id_busqueda = int(id_busqueda)

        while i < total and indice_encontrado == -1:
            entrada = lista[i]
            valor_id = entrada.get("id_usuario")

            # Se compara el valor del id tal cual (normalmente entero).
            if valor_id == id_busqueda:
                indice_encontrado = i

            i = i + 1

        # Si no se encontró ningún usuario con ese ID, se informa y se sale.
        if indice_encontrado == -1:
            print("\nNo existe ningún usuario con el ID:", id_busqueda)
            return

        # Mostramos al administrador qué usuario se va a eliminar.
        usuario_json = lista[indice_encontrado]
        nombre_login = usuario_json.get("nombre_usuario") or usuario_json.get("nombre")
        rol = usuario_json.get("rol")

        print("\nSe va a eliminar el siguiente usuario del archivo JSON:")
        print("ID:", usuario_json.get("id_usuario"), "| Usuario:", nombre_login, "| Rol:", rol)

        # Pedimos confirmación explícita al administrador.
        print("Esta acción es permanente. Se eliminará del JSON.")
        confirmacion = input("¿Confirmar eliminación? (S/N): ").strip().upper()

        if confirmacion != "S":
            # Si el administrador no confirma con 'S', se cancela la operación.
            print("\nOperación cancelada por el administrador.")
            return

        # Creamos una nueva lista de usuarios sin el elemento a eliminar.
        nueva_lista = []
        j = 0
        while j < total:
            if j != indice_encontrado:
                nueva_lista.append(lista[j])
            j = j + 1

        # Reemplazamos la lista antigua por la nueva en la estructura de datos.
        datos["usuarios"] = nueva_lista

        # Escribimos el JSON actualizado en el archivo.
        f2 = None
        try:
            f2 = open(self.ruta_usuarios, "w", encoding="utf-8")
            texto = json.dumps(datos, ensure_ascii=False, indent=4)
            f2.write(texto)
        except Exception as e:
            print("\nError al escribir el archivo de usuarios:", str(e))
            return

        if f2 is not None:
            f2.close()

        # Recargamos los datos en memoria para que self.usuarios se actualice.
        self.cargar_datos()

        print("\nUsuario eliminado correctamente del sistema.")

# =============================================================================
# Funciones para trabajar con el JSON de salas y su estado de ocupación
# Archivo: sensores_habitaciones.json
# Estructura esperada:
# {
#   "habitaciones": {
#       "id_habitacion": [1, 2, 3, ...],
#       "estado": ["libre", "ocupado", ...]
#   }
# }
# =============================================================================

def visualizar_estado_sala(ruta_sensores="sensores_habitaciones.json"):
    # Muestra por pantalla el estado de una sala a partir de su id_habitacion.

    datos = None
    f = None

    try:
        f = open(ruta_sensores, "r", encoding="utf-8")
        datos = json.load(f)
    except FileNotFoundError:
        print("\nNo se encontró el archivo de sensores/habitaciones:", ruta_sensores)
        if f is not None:
            f.close()
        return

    if f is not None:
        f.close()

    # Se comprueba que la estructura del JSON sea la esperada.
    habitaciones = datos.get("habitaciones")
    if not isinstance(habitaciones, dict):
        print("\nLa estructura del archivo de sensores no es válida.")
        return

    lista_ids = habitaciones.get("id_habitacion")
    lista_estados = habitaciones.get("estado")

    if not isinstance(lista_ids, list) or not isinstance(lista_estados, list):
        print("\nLa estructura de habitaciones no contiene listas válidas.")
        return

    if len(lista_ids) != len(lista_estados):
        print("\nLas listas de id_habitacion y estado no tienen la misma longitud.")
        return

    # Se pide el id de la habitación al usuario.
    id_texto = input("\nIntroduce el id_habitacion: ").strip()
    if not id_texto.isdigit():
        print("El id_habitacion debe ser un número entero.")
        return

    id_habitacion = int(id_texto)

    # Banderas para la búsqueda.
    encontrado = False
    estado_encontrado = None

    # Búsqueda manual sin usar 'break'.
    i = 0
    total = len(lista_ids)
    while i < total and not encontrado:
        if lista_ids[i] == id_habitacion:
            encontrado = True
            estado_encontrado = lista_estados[i]
        else:
            i = i + 1

    if encontrado:
        print("El estado actual de la sala", id_habitacion, "es:", estado_encontrado)
    else:
        print("La habitación con id", id_habitacion, "no existe.")


def cambiar_estado_ocupacion_sala(ruta_sensores="sensores_habitaciones.json"):
    # Permite cambiar el estado de ocupación de una sala (libre/ocupado)
    # pidiendo confirmación al usuario y guardando el cambio en el JSON.

    datos = None
    f = None

    try:
        f = open(ruta_sensores, "r", encoding="utf-8")
        datos = json.load(f)
    except FileNotFoundError:
        print("\nNo se encontró el archivo de sensores/habitaciones:", ruta_sensores)
        if f is not None:
            f.close()
        return

    if f is not None:
        f.close()

    habitaciones = datos.get("habitaciones")
    if not isinstance(habitaciones, dict):
        print("\nLa estructura del archivo de sensores no es válida.")
        return

    lista_ids = habitaciones.get("id_habitacion")
    lista_estados = habitaciones.get("estado")

    if not isinstance(lista_ids, list) or not isinstance(lista_estados, list):
        print("\nLa estructura de habitaciones no contiene listas válidas.")
        return

    if len(lista_ids) != len(lista_estados):
        print("\nLas listas de id_habitacion y estado no tienen la misma longitud.")
        return

    # Petición del id de la habitación.
    id_texto = input("\nIntroduce el id_habitacion: ").strip()
    if not id_texto.isdigit():
        print("El id_habitacion debe ser un número entero.")
        return

    id_habitacion = int(id_texto)

    # Búsqueda del índice de la habitación.
    indice_encontrado = -1
    i = 0
    total = len(lista_ids)
    while i < total and indice_encontrado == -1:
        if lista_ids[i] == id_habitacion:
            indice_encontrado = i
        else:
            i = i + 1

    if indice_encontrado == -1:
        print("La habitación con id", id_habitacion, "no existe.")
        return

    # Estado actual y nuevo estado propuesto.
    estado_actual = lista_estados[indice_encontrado]
    print("El estado actual de la sala", id_habitacion, "es:", estado_actual)

    if estado_actual == "ocupado":
        nuevo_estado = "libre"
    else:
        nuevo_estado = "ocupado"

    # Confirmación del usuario.
    fin_pregunta = False
    respuesta = None
    while not fin_pregunta:
        respuesta = input("¿Desea cambiar el estado a " + nuevo_estado + "? (Si/No): ").strip()
        if respuesta == "Si" or respuesta == "No":
            fin_pregunta = True
        else:
            print("La respuesta introducida es errónea, debe introducir Si o No.")

    if respuesta == "No":
        print("No se ha realizado ningún cambio.")
        return

    # Se actualiza el estado en la lista.
    lista_estados[indice_encontrado] = nuevo_estado

    # Se guarda el JSON actualizado en disco.
    f2 = None
    try:
        f2 = open(ruta_sensores, "w", encoding="utf-8")
        texto = json.dumps(datos, ensure_ascii=False, indent=4)
        f2.write(texto)
    except Exception as e:
        print("\nError al escribir el archivo de sensores/habitaciones:", str(e))
        if f2 is not None:
            f2.close()
        return

    if f2 is not None:
        f2.close()

    print("Datos actualizados correctamente.")
    print("El estado actual de la sala", id_habitacion, "es ahora:", nuevo_estado)
