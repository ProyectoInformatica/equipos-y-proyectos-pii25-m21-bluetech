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
import os   # Para comprobar la existencia del JSON de parámetros de sanidad

# Ruta del archivo con los valores comparativos de sanidad
RUTA_VALORES_COMPARATIVOS = "valores_comparativos.json"

# Clase que define los tipos de roles posibles para un usuario.
class Rol:
    ADMINISTRADOR = "administrador"
    TRABAJADOR = "trabajador"


# Clase que representa un usuario del sistema (como administrador o trabajador).
class Usuario:
    def __init__(self, id_usuario, nombre_usuario, contrasena_hash, rol, num_registros=0, estado=1):
        # Constructor que inicializa los atributos básicos del usuario.
        # En este caso, 'contrasena_hash' almacena el hash SHA-256 de la contraseña,
        # no la contraseña en texto plano.
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasena_hash = contrasena_hash
        self.rol = rol

        # >>> CAMBIO MÍNIMO: atributos necesarios para el control de acceso / cambio de contraseña
        self.num_registros = num_registros
        self.estado = estado

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
                        rol=rol_normalizado,

                        # >>> CAMBIO MÍNIMO: cargar control de estado/contador desde JSON (o defaults)
                        num_registros=u.get("num_registros", 0),
                        estado=u.get("estado", 1)
                    )

                    # Se agrega el usuario a la lista general de usuarios (admins y trabajadores).
                    self.usuarios.append(nuevo)

                j = j + 1

        except FileNotFoundError:
            # Si no se encuentra el archivo, se muestra un mensaje.
            print("No se encontró el archivo de usuarios:", self.ruta_usuarios)

        if f2 is not None:
            f2.close()  # Se cierra el archivo si fue abierto correctamente.

    def verificar_login(self, usuario, contrasena):
        """
        Verifica credenciales sin rol explícito.
        El rol se obtiene del JSON.
        """
        hash_pass = hashlib.sha256(contrasena.encode()).hexdigest()

        for u in self.usuarios:
            if (
                u.nombre_usuario == usuario
                and u.contrasena_hash == hash_pass
            ):
                return u

        return None


    def guardar_cambios(self):
        # Guarda en el JSON los cambios de credenciales/estado realizados sobre los objetos Usuario.
        # Se actualizan solo los campos necesarios: contrasena_hash, num_registros, estado (y campos básicos si existieran).
        datos = None
        f = None
        try:
            f = open(self.ruta_usuarios, "r", encoding="utf-8")
            datos = json.load(f)
        except FileNotFoundError:
            print("No se encontró el archivo de usuarios:", self.ruta_usuarios)
            return False
        except Exception as e:
            print("Error al leer el archivo de usuarios:", str(e))
            return False
        finally:
            if f is not None:
                f.close()

        if not isinstance(datos, dict):
            print("El formato del archivo de usuarios no es válido.")
            return False

        lista = datos.get("usuarios", [])
        if not isinstance(lista, list):
            print("La estructura del archivo de usuarios no es válida.")
            return False

        i = 0
        total = len(lista)
        while i < total:
            entrada = lista[i]
            if isinstance(entrada, dict):
                id_json = entrada.get("id_usuario")
                if isinstance(id_json, str) and id_json.isdigit():
                    id_json = int(id_json)

                nombre_json = entrada.get("nombre_usuario") or entrada.get("nombre")

                # buscar coincidencia en memoria
                j = 0
                total_mem = len(self.usuarios)
                encontrado = False

                while j < total_mem and not encontrado:
                    u_obj = self.usuarios[j]

                    # Normalizar id en memoria también por si acaso
                    id_mem = u_obj.id_usuario
                    if isinstance(id_mem, str) and id_mem.isdigit():
                        id_mem = int(id_mem)

                    # 1) Match por id_usuario
                    if id_json is not None and id_mem is not None and id_mem == id_json:
                        encontrado = True

                    # 2) Fallback por nombre de usuario (si el ID viniera raro)
                    elif nombre_json is not None and isinstance(nombre_json, str):
                        if u_obj.nombre_usuario == nombre_json:
                            encontrado = True

                    if encontrado:
                        # Actualizar solo lo necesario
                        entrada["contrasena_hash"] = u_obj.contrasena_hash
                        entrada["num_registros"] = u_obj.num_registros
                        entrada["estado"] = u_obj.estado

                        # Mantener consistencia de nombre/rol si están presentes
                        if "nombre_usuario" in entrada:
                            entrada["nombre_usuario"] = u_obj.nombre_usuario
                        if "rol" in entrada:
                            entrada["rol"] = u_obj.rol

                    j = j + 1

            i = i + 1

        f2 = None
        try:
            f2 = open(self.ruta_usuarios, "w", encoding="utf-8")
            texto = json.dumps(datos, ensure_ascii=False, indent=4)
            f2.write(texto)
        except Exception as e:
            print("Error al escribir el archivo de usuarios:", str(e))
            return False
        finally:
            if f2 is not None:
                f2.close()

        return True


    def eliminar_usuario_por_id(self, id_usuario, pedir_confirmacion_por_consola=True):
        """
        Elimina un usuario del sistema a partir de su ID.

        - Si pedir_confirmacion_por_consola=True  -> funciona como hasta ahora (modo consola),
          mostrando mensajes y pidiendo confirmación con input().
        - Si pedir_confirmacion_por_consola=False -> NO pide nada por consola ni imprime;
          simplemente intenta borrar y devuelve True/False.

        Devuelve:
            True  si se ha eliminado el usuario.
            False si no existe el ID o ha habido algún problema.
        """

        # 1) Leer archivo JSON de usuarios
        datos = None
        f = None

        try:
            f = open(self.ruta_usuarios, "r", encoding="utf-8")
            datos = json.load(f)
        except FileNotFoundError:
            if pedir_confirmacion_por_consola:
                print("\nNo se encontró el archivo de usuarios:", self.ruta_usuarios)
            return False
        finally:
            if f is not None:
                f.close()

        if not isinstance(datos, dict):
            if pedir_confirmacion_por_consola:
                print("\nEl formato del archivo de usuarios no es válido.")
            return False

        lista = datos.get("usuarios", [])
        if not isinstance(lista, list):
            if pedir_confirmacion_por_consola:
                print("\nLa estructura del archivo de usuarios no es válida.")
            return False

        # 2) Normalizar ID y buscar en la lista
        id_busqueda = id_usuario
        if isinstance(id_busqueda, str) and id_busqueda.isdigit():
            id_busqueda = int(id_busqueda)

        indice_encontrado = -1
        i = 0
        total = len(lista)

        while i < total and indice_encontrado == -1:
            entrada = lista[i]
            if isinstance(entrada, dict) and entrada.get("id_usuario") == id_busqueda:
                indice_encontrado = i
            i += 1

        if indice_encontrado == -1:
            if pedir_confirmacion_por_consola:
                print("\nNo existe ningún usuario con el ID:", id_busqueda)
            return False

        usuario_json = lista[indice_encontrado]
        nombre_login = usuario_json.get("nombre_usuario") or usuario_json.get("nombre")
        rol = usuario_json.get("rol")

        # 3) Confirmación SOLO en modo consola
        if pedir_confirmacion_por_consola:
            print("\nSe va a eliminar el siguiente usuario del archivo JSON:")
            print("ID:", usuario_json.get("id_usuario"), "| Usuario:", nombre_login, "| Rol:", rol)
            print("Esta acción es permanente. Se eliminará del JSON.")
            confirmacion = input("¿Confirmar eliminación? (S/N): ").strip().upper()

            if confirmacion != "S":
                print("\nOperación cancelada por el administrador.")
                return False

        # 4) Construir nueva lista sin el usuario
        nueva_lista = []
        j = 0
        while j < total:
            if j != indice_encontrado:
                nueva_lista.append(lista[j])
            j += 1

        datos["usuarios"] = nueva_lista

        # 5) Guardar JSON actualizado
        f2 = None
        try:
            f2 = open(self.ruta_usuarios, "w", encoding="utf-8")
            texto = json.dumps(datos, ensure_ascii=False, indent=4)
            f2.write(texto)
        except Exception as e:
            if pedir_confirmacion_por_consola:
                print("\nError al escribir el archivo de usuarios:", str(e))
            return False
        finally:
            if f2 is not None:
                f2.close()

        # 6) Recargar usuarios en memoria
        self.cargar_datos()

        if pedir_confirmacion_por_consola:
            print("\nUsuario eliminado correctamente del sistema.")

        return True

    def agregar_trabajador(self, nombre, apellidos, nombre_usuario, contrasena):
        
        # --- 1. Generar ID único automático ---
        max_id = 0
        i = 0
        total = len(self.usuarios)
        while i < total:
            if self.usuarios[i].id_usuario > max_id:
                max_id = self.usuarios[i].id_usuario
            i = i + 1
        nuevo_id = max_id + 1

        # --- 2. Mostrar resumen al administrador ---
        print("\n" + "="*55)
        print("       NUEVO TRABAJADOR A REGISTRAR")
        print("="*55)
        print(f"ID asignado       : {nuevo_id}")
        print(f"Nombre            : {nombre}")
        print(f"Apellidos         : {apellidos}")
        print(f"Nombre de usuario : {nombre_usuario}")
        print(f"Contraseña        : {contrasena}")
        print(f"Rol               : trabajador")
        print("="*55)

        # --- 3. Confirmación obligatoria ---
        confirmacion = input("\n¿Confirmar creación del trabajador? (S/N): ").strip().upper()
        if confirmacion != "S":
            print("\nOperación cancelada.")
            return False

        # --- 4. Leer el archivo JSON actual ---
        datos = None
        f = None
        try:
            f = open(self.ruta_usuarios, "r", encoding="utf-8")
            datos = json.load(f)
        except FileNotFoundError:
            print(f"\nArchivo no encontrado. Se creará uno nuevo: {self.ruta_usuarios}")
            datos = {"usuarios": []}
        finally:
            if f is not None:
                f.close()

        # --- 5. Crear el nuevo trabajador (solo campo "contraseña") ---
        nuevo_trabajador = {
            "id_usuario": nuevo_id,
            "nombre": nombre,
            "apellidos": apellidos,
            "nombre_usuario": nombre_usuario,
            "contraseña": contrasena,        # <-- SOLO ESTE CAMPO, como el resto del JSON
            "rol": "trabajador"
        }

        # --- 6. Añadir a la lista ---
        if "usuarios" not in datos:
            datos["usuarios"] = []
        datos["usuarios"].append(nuevo_trabajador)

        # --- 7. Guardar en disco ---
        f2 = None
        try:
            f2 = open(self.ruta_usuarios, "w", encoding="utf-8")
            json.dump(datos, f2, ensure_ascii=False, indent=4)
            print(f"\nTrabajador '{nombre_usuario}' creado correctamente con ID {nuevo_id}.")
        except Exception as e:
            print(f"\nError al guardar el archivo: {e}")
            return False
        finally:
            if f2 is not None:
                f2.close()

        # --- 8. Recargar datos en memoria ---
        self.cargar_datos()
        return True

# =============================================================================
# Funciones para trabajar con el JSON de salas y su estado de ocupación
# Archivo: habitacion.json
# Estructura esperada:
# {
#   "habitaciones": {
#       "id_habitacion": [1, 2, 3, ...],
#       "estado": ["libre", "ocupado", ...]
#   }
# }
# =============================================================================
def visualizar_estado_sala(ruta_sensores="habitacion.json"):
    # Muestra por pantalla el estado de una sala a partir de su id_habitacion.
    #Se realiza la lectura del json de habitaciones y sensores
    with open("habitacion.json", "r") as archivo:
        datos = json.load(archivo)

    #Solicita al usuario el id_habitación
    id_habitacion = input("Introduce el id_habitacion: ")
    id_habitacion = int(id_habitacion)

    #Variable para la longitud del array de id_habitaciones del json
    longitud = len(datos["habitaciones"]["id_habitacion"])

    #verifica que el id sea mayor que 0 y este en el array ya que van en orden
    if id_habitacion <= longitud and id_habitacion > 0:
        #recorre el array de id_habitacion
        for i in range (longitud):
            #verifica que uno de ellos coincida
            if datos["habitaciones"]["id_habitacion"][i] == id_habitacion:
                #Muestra el estado actual de la sala
                data = datos["habitaciones"]["estado"][i]
                print(f"El estado actual de la sala {id_habitacion} es: {data}")
    else:
        #Error al encontrar el id
        print(f"La habitación con id {id_habitacion} no existe.")

def cambiar_estado_ocupacion_sala(ruta_sensores="habitacion.json"):
    # Permite cambiar el estado de ocupación de una sala (libre/ocupado)
    # pidiendo confirmación al usuario y guardando el cambio en el JSON.

    #Se realiza la lectura del json de habitaciones y sensores
    with open("habitacion.json", "r") as archivo:
        datos = json.load(archivo)

    #Introduce el usuario el id_habitación
    id_habitacion = input("Introduce el id_habitacion: ")
    id_habitacion = int(id_habitacion)

    #Variable para la longitud del array de id_habitaciones del json
    longitud = len(datos["habitaciones"]["id_habitacion"])

    #verifica que el id sea mayor que 0 y este en el array ya que van en orden
    if id_habitacion <= longitud and id_habitacion > 0:
        #recorre el array de id_habitacion
        for i in range (longitud):
            #verifica que uno de ellos coincida
            if datos["habitaciones"]["id_habitacion"][i] == id_habitacion:
                #Muestra el estado actual de la sala
                data = datos["habitaciones"]["estado"][i]
                print(f"El estado actual de la sala {id_habitacion} es: {data}")
                #En caso de estar ocupado el nuevo dato sera libre y a la inversa en caso contrario
                if data == "ocupado":
                    nuevo_dato = "libre"
                else:
                    nuevo_dato = "ocupado"
                fin = False
                #Se ejecuta siempre que no se cumpla la respuesta del usuario con lo solicitado
                while not fin:
                    #Almacena en una variable la respuesta del usuario a la pregunta solicitada
                    respuesta = input(f"¿Desea cambiar el estado a {nuevo_dato}? (Si/No)")
                    respuesta = str(respuesta)
                    #En caso de que la respuesta sea Si cambia el estado en caso contrario lo deja igual
                    if respuesta == "Si":
                        datos["habitaciones"]["estado"][i] = nuevo_dato
                        fin = True
                    elif respuesta == "No":
                        datos["habitaciones"]["estado"][i] = data
                        fin = True
                    #En caso de respuesta erronea salta error y vuelve a solicitar una respuesta
                    else:
                        print("La respuesta introducida es erronea, debe introducir Si o No.")
                #Sobreescribe el archivo json de habitaciones y sensores con las modificaciones correspondientes
                with open("habitacion.json", "w") as archivo:
                    json.dump(datos, archivo, indent=4)
                #Confirma que los datos se han actualizado y le vueleve a mostrar el resultado actualizado del estado
                print("Datos actualizados correctamente")
                nuevo_data = datos["habitaciones"]["estado"][i]
                print(f"El estado actual de la sala {id_habitacion} es: {nuevo_data}")
    else:
        #Error al encontrar el id
        print(f"La habitación con id {id_habitacion} no existe.")

# =============================================================================
# FUNCIONES PARA CARGAR Y GUARDAR VALORES COMPARATIVOS DE SANIDAD
# Estructura esperada del JSON valores_comparativos.json:
# {
#     "s_temperatura": 0,
#     "s_humedad": 0,
#     "s_calidad_aire": {
#         "PM2.5": 0,
#         "PM10": 0,
#         "CO": 0,
#         "NO2": 0,
#         "CO2": 0,
#         "TVOC": 0
#     }
# }
# =============================================================================

def cargar_valores_comparativos(ruta=RUTA_VALORES_COMPARATIVOS):
    # Lee el archivo JSON de valores comparativos y devuelve un diccionario.
    datos = {}
    existe = os.path.exists(ruta)

    if not existe:
        print("\n[ERROR] No se encontró el archivo de valores comparativos:", ruta)
        return {}

    f = None
    try:
        f = open(ruta, "r", encoding="utf-8")
        datos = json.load(f)
    except Exception as e:
        print("\n[ERROR] No se pudo cargar el archivo de valores comparativos:", str(e))
        datos = {}
    if f is not None:
        f.close()

    if isinstance(datos, dict):
        return datos
    else:
        print("\n[ERROR] El contenido de valores_comparativos.json no es un diccionario.")
        return {}


def guardar_valores_comparativos(data, ruta=RUTA_VALORES_COMPARATIVOS):
    # Guarda en disco el diccionario de valores comparativos.
    f = None
    try:
        f = open(ruta, "w", encoding="utf-8")
        texto = json.dumps(data, ensure_ascii=False, indent=4)
        f.write(texto)
    except Exception as e:
        print("\n[ERROR] No se pudo escribir el archivo de valores comparativos:", str(e))
        if f is not None:
            f.close()
        return False

    if f is not None:
        f.close()

    return True

def consultar_parametros_sanidad(parametro=None):
    # Consulta los valores comparativos de sanidad.
    # parametro:
    #   - None          -> devuelve todo el contenido del JSON
    #   - "temperatura" -> devuelve solo s_temperatura
    #   - "humedad"     -> devuelve solo s_humedad
    #   - nombre de parámetro de calidad del aire (ej: "PM2.5", "CO2")

    datos = cargar_valores_comparativos()
    if not datos:
        return {"error": "No se han podido cargar los valores del JSON."}

    # Sin parámetro: devolver todo el JSON
    if parametro is None:
        return datos

    texto = parametro.strip()
    parametro_minus = texto.lower()

    # Mapear nombres lógicos a claves del JSON
    if parametro_minus == "temperatura" or parametro_minus == "s_temperatura":
        resultado = {}
        resultado["s_temperatura"] = datos.get("s_temperatura")
        return resultado

    if parametro_minus == "humedad" or parametro_minus == "s_humedad":
        resultado = {}
        resultado["s_humedad"] = datos.get("s_humedad")
        return resultado

    # Buscar en s_calidad_aire
    calidad = datos.get("s_calidad_aire")
    if not isinstance(calidad, dict):
        return {"error": "La sección 's_calidad_aire' no existe o no es válida en el JSON."}

    claves = list(calidad.keys())
    i = 0
    total = len(claves)
    nombre_real = None

    while i < total and nombre_real is None:
        clave_actual = claves[i]
        if isinstance(clave_actual, str):
            if clave_actual.lower() == parametro_minus:
                nombre_real = clave_actual
        i = i + 1

    if nombre_real is None:
        return {"error": "El parámetro '" + texto + "' no existe en s_calidad_aire."}

    resultado = {}
    resultado[nombre_real] = calidad.get(nombre_real)
    return resultado


def mostrar_tabla_parametros_sanidad(diccionario):
    # Muestra por pantalla los valores comparativos de sanidad de forma ordenada.

    if not isinstance(diccionario, dict):
        print("\n[ERROR] Estructura de datos no válida al mostrar parámetros.")
        return

    if "error" in diccionario:
        print("\n[ERROR] " + str(diccionario["error"]))
        return

    print("\n=========== PARÁMETROS DE SANIDAD (COMPARATIVOS) ===========\n")

    # Si se ha pedido todo el JSON (s_temperatura, s_humedad y s_calidad_aire)
    if "s_calidad_aire" in diccionario:
        # Mostrar s_temperatura si existe
        if "s_temperatura" in diccionario:
            print("s_temperatura:", diccionario.get("s_temperatura"))
        # Mostrar s_humedad si existe
        if "s_humedad" in diccionario:
            print("s_humedad:", diccionario.get("s_humedad"))

        # Mostrar todos los parámetros de s_calidad_aire
        calidad = diccionario.get("s_calidad_aire")
        if isinstance(calidad, dict):
            print("\n--- s_calidad_aire ---\n")
            claves = list(calidad.keys())
            i = 0
            total = len(claves)
            while i < total:
                clave = claves[i]
                valor = calidad.get(clave)
                print(clave + ":", valor)
                i = i + 1
    else:
        # Se ha pedido un subconjunto: por ejemplo solo s_temperatura,
        # solo s_humedad o un parámetro de calidad del aire.
        claves_dic = list(diccionario.keys())
        i = 0
        total = len(claves_dic)
        while i < total:
            clave = claves_dic[i]
            valor = diccionario.get(clave)
            print(str(clave) + ":", valor)
            i = i + 1

    print("\n=============================================================\n")

def consultar_parametros_sanidad_interactivo():
    # Menú interactivo para consultar los valores comparativos de sanidad.

    print("\n=== CONSULTA DE PARÁMETROS DE SANIDAD ===")
    print("1. Ver todos los parámetros")
    print("2. Ver parámetro de temperatura (s_temperatura)")
    print("3. Ver parámetro de humedad (s_humedad)")
    print("4. Ver un parámetro de calidad del aire (s_calidad_aire)")
    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        resultado = consultar_parametros_sanidad()
        mostrar_tabla_parametros_sanidad(resultado)
    elif opcion == "2":
        resultado = consultar_parametros_sanidad("temperatura")
        mostrar_tabla_parametros_sanidad(resultado)
    elif opcion == "3":
        resultado = consultar_parametros_sanidad("humedad")
        mostrar_tabla_parametros_sanidad(resultado)
    elif opcion == "4":
        nombre = input("Introduce el nombre del parámetro de calidad del aire (ej: PM2.5, CO2): ").strip()
        resultado = consultar_parametros_sanidad(nombre)
        mostrar_tabla_parametros_sanidad(resultado)
    else:
        print("\nOpción no válida en la consulta de parámetros de sanidad.")

def cambiar_parametros_sanidad_interactivo():
    # Menú interactivo para modificar los valores comparativos de sanidad.
    # Se basa en el archivo valores_comparativos.json.

    datos = cargar_valores_comparativos()
    if not datos:
        return

    print("\n=== CATEGORÍAS DISPONIBLES EN valores_comparativos.json ===")
    claves_categorias = list(datos.keys())
    i = 0
    total_cat = len(claves_categorias)
    indice = 1
    while i < total_cat:
        print(str(indice) + ". " + str(claves_categorias[i]))
        i = i + 1
        indice = indice + 1

    opcion_texto = input("\nSeleccione una categoría (número): ").strip()
    if not opcion_texto.isdigit():
        print("Opción inválida.")
        return

    opcion_num = int(opcion_texto)
    if opcion_num < 1 or opcion_num > total_cat:
        print("Opción inválida.")
        return

    categoria = claves_categorias[opcion_num - 1]

    # Caso 1: s_temperatura o s_humedad (valores simples)
    if categoria == "s_temperatura" or categoria == "s_humedad":
        valor_actual = datos.get(categoria)
        print("\nValor actual de " + categoria + ":", valor_actual)
        nuevo_valor_texto = input("Nuevo valor (normalmente 0, 1 o 2): ").strip()

        # Intentar convertir a número
        nuevo_valor = None
        if nuevo_valor_texto.isdigit():
            nuevo_valor = int(nuevo_valor_texto)
        else:
            nuevo_valor = nuevo_valor_texto

        datos[categoria] = nuevo_valor

    # Caso 2: s_calidad_aire (diccionario con varios parámetros)
    elif categoria == "s_calidad_aire":
        bloque = datos.get("s_calidad_aire")
        if not isinstance(bloque, dict):
            print("La categoría s_calidad_aire no tiene una estructura válida.")
            return

        print("\n=== Parámetros de s_calidad_aire ===")
        claves_param = list(bloque.keys())
        i = 0
        total_param = len(claves_param)
        indice = 1
        while i < total_param:
            print(str(indice) + ". " + str(claves_param[i]))
            i = i + 1
            indice = indice + 1

        opcion_param_texto = input("\nSeleccione un parámetro (número): ").strip()
        if not opcion_param_texto.isdigit():
            print("Opción inválida.")
            return

        opcion_param_num = int(opcion_param_texto)
        if opcion_param_num < 1 or opcion_param_num > total_param:
            print("Opción inválida.")
            return

        param_seleccionado = claves_param[opcion_param_num - 1]
        valor_actual = bloque.get(param_seleccionado)
        print("\nValor actual de " + param_seleccionado + ":", valor_actual)

        nuevo_valor_texto = input("Nuevo valor (normalmente 0, 1 o 2): ").strip()

        nuevo_valor = None
        if nuevo_valor_texto.isdigit():
            nuevo_valor = int(nuevo_valor_texto)
        else:
            nuevo_valor = nuevo_valor_texto

        bloque[param_seleccionado] = nuevo_valor
        datos["s_calidad_aire"] = bloque

    else:
        # Si en el futuro hubiera más claves, se podría gestionar aquí.
        print("Categoría no reconocida para edición.")
        return

    correcto = guardar_valores_comparativos(datos)
    if correcto:
        print("\nParámetro actualizado correctamente.")
    else:
        print("\nNo se pudo guardar la actualización en el archivo.")
