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

    # Se realiza la lectura del json de habitaciones y sensores.
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

    # Se comprueba que exista la clave "habitaciones" con la estructura esperada.
    habitaciones = datos.get("habitaciones")
    if not isinstance(habitaciones, dict):
        print("\nLa estructura del archivo de sensores no es válida.")
        return

    lista_ids = habitaciones.get("id_habitacion")
    lista_estados = habitaciones.get("estado")

    if not isinstance(lista_ids, list) or not isinstance(lista_estados, list):
        print("\nLa estructura de habitaciones no contiene listas válidas.")
        return

    longitud = len(lista_ids)

    # Solicita al usuario el id_habitacion.
    id_texto = input("Introduce el id_habitacion: ").strip()
    if not id_texto.isdigit():
        print("El id_habitacion debe ser un número entero.")
        return

    id_habitacion = int(id_texto)

    # Verifica que el id sea mayor que 0 y esté dentro del rango (asumiendo ids secuenciales).
    if id_habitacion <= longitud and id_habitacion > 0:
        # Recorre el array de id_habitacion para encontrar el índice correcto.
        i = 0
        encontrado = False
        estado_encontrado = None

        while i < longitud and not encontrado:
            if lista_ids[i] == id_habitacion:
                encontrado = True
                estado_encontrado = lista_estados[i]
            else:
                i = i + 1

        if encontrado:
            # Muestra el estado actual de la sala.
            print("El estado actual de la sala", id_habitacion, "es:", estado_encontrado)
        else:
            # Caso raro: el id está dentro del rango pero no aparece en la lista.
            print("La habitación con id", id_habitacion, "no existe.")
    else:
        # Error al encontrar el id (fuera de rango).
        print("La habitación con id", id_habitacion, "no existe.")

def cambiar_estado_ocupacion_sala(ruta_sensores="sensores_habitaciones.json"):
    # Permite cambiar el estado de ocupación de una sala (libre/ocupado)
    # pidiendo confirmación al usuario y guardando el cambio en el JSON.

    datos = None
    f = None

    # Se realiza la lectura del json de habitaciones y sensores.
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

    longitud = len(lista_ids)

    # Introduce el usuario el id_habitacion.
    id_texto = input("Introduce el id_habitacion: ").strip()
    if not id_texto.isdigit():
        print("El id_habitacion debe ser un número entero.")
        return

    id_habitacion = int(id_texto)

    # Verifica que el id sea mayor que 0 y esté en el array (asumiendo orden secuencial).
    if id_habitacion <= longitud and id_habitacion > 0:
        # Recorre el array de id_habitacion para encontrar el índice.
        i = 0
        indice_encontrado = -1

        while i < longitud and indice_encontrado == -1:
            if lista_ids[i] == id_habitacion:
                indice_encontrado = i
            else:
                i = i + 1

        if indice_encontrado == -1:
            # Caso raro: está dentro del rango pero no lo encuentra.
            print("La habitación con id", id_habitacion, "no existe.")
            return

        # Muestra el estado actual de la sala.
        data = lista_estados[indice_encontrado]
        print("El estado actual de la sala", id_habitacion, "es:", data)

        # En caso de estar ocupado el nuevo dato será libre y a la inversa en caso contrario.
        if data == "ocupado":
            nuevo_dato = "libre"
        else:
            nuevo_dato = "ocupado"

        # Se ejecuta siempre que no se cumpla la respuesta del usuario con lo solicitado.
        fin = False
        while not fin:
            # Almacena en una variable la respuesta del usuario a la pregunta solicitada.
            respuesta = input("¿Desea cambiar el estado a " + nuevo_dato + "? (Si/No): ").strip()
            respuesta = str(respuesta)

            # En caso de que la respuesta sea "Si", cambia el estado; en caso contrario lo deja igual.
            if respuesta == "Si":
                lista_estados[indice_encontrado] = nuevo_dato
                fin = True
            elif respuesta == "No":
                lista_estados[indice_encontrado] = data
                fin = True
            else:
                # En caso de respuesta errónea salta error y vuelve a solicitar una respuesta.
                print("La respuesta introducida es errónea, debe introducir Si o No.")

        # Sobrescribe el archivo json de habitaciones y sensores con las modificaciones correspondientes.
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

        # Confirma que los datos se han actualizado y vuelve a mostrar el estado actualizado.
        print("Datos actualizados correctamente")
        nuevo_data = lista_estados[indice_encontrado]
        print("El estado actual de la sala", id_habitacion, "es:", nuevo_data)
    else:
        # Error al encontrar el id.
        print("La habitación con id", id_habitacion, "no existe.")

# =============================================================================
# Funciones para consultar y modificar parámetros de sanidad
# Archivo: valores_recomendados.json
# Estructura esperada:
#   - temperatura: {min, max, unidad, descripcion}
#   - humedad: {min, max, unidad, descripcion}
#   - calidad_aire: { "PM2.5": {max, unidad, descripcion}, ... }
# =============================================================================

def cargar_valores_recomendados_sanidad(ruta="valores_recomendados.json"):
    # Lee el archivo JSON de valores recomendados de sanidad.
    datos = None
    f = None

    try:
        f = open(ruta, "r", encoding="utf-8")
        datos = json.load(f)
    except FileNotFoundError:
        print("\nNo se encontró el archivo de valores recomendados:", ruta)
        if f is not None:
            f.close()
        return {}
    except Exception as e:
        print("\nError al leer el archivo de valores recomendados:", str(e))
        if f is not None:
            f.close()
        return {}

    if f is not None:
        f.close()

    if isinstance(datos, dict):
        return datos
    else:
        print("\nEl contenido de valores_recomendados.json no es un diccionario.")
        return {}


def guardar_valores_recomendados_sanidad(data, ruta="valores_recomendados.json"):
    # Escribe en disco el diccionario de valores recomendados actualizado.
    f = None

    try:
        f = open(ruta, "w", encoding="utf-8")
        texto = json.dumps(data, ensure_ascii=False, indent=4)
        f.write(texto)
    except Exception as e:
        print("\nError al escribir el archivo de valores recomendados:", str(e))
        if f is not None:
            f.close()
        return False

    if f is not None:
        f.close()

    return True

def consultar_parametros_sanidad(parametro=None, ruta="valores_recomendados.json"):
    # Devuelve un diccionario con los valores recomendados.
    # parametro:
    #   - None        -> todo el contenido
    #   - "temperatura" o "humedad"
    #   - nombre de un parámetro de calidad del aire (ej: "PM2.5", "CO2")

    datos = cargar_valores_recomendados_sanidad(ruta)
    if not datos:
        return {"error": "No se han podido cargar los valores del JSON."}

    if parametro is None:
        return datos

    parametro = parametro.strip().lower()

    # Temperatura u humedad
    if parametro == "temperatura" or parametro == "humedad":
        valor = datos.get(parametro)
        if isinstance(valor, dict):
            resultado = {}
            resultado[parametro] = valor
            return resultado
        else:
            return {"error": "El parámetro '" + parametro + "' no existe en el JSON."}

    # Calidad del aire
    calidad = datos.get("calidad_aire", {})
    if not isinstance(calidad, dict):
        return {"error": "La sección 'calidad_aire' no existe o no es válida."}

    # Búsqueda manual sin for
    claves = list(calidad.keys())
    i = 0
    total = len(claves)
    nombre_real = None
    while i < total and nombre_real is None:
        clave_actual = claves[i]
        if isinstance(clave_actual, str):
            if clave_actual.lower() == parametro:
                nombre_real = clave_actual
        i = i + 1

    if nombre_real is None:
        return {"error": "El parámetro '" + parametro + "' no existe en calidad_aire."}

    resultado = {}
    resultado[nombre_real] = calidad.get(nombre_real)
    return resultado


def mostrar_tabla_parametros_sanidad(diccionario):
    # Muestra por pantalla la información de parámetros de sanidad de forma ordenada.

    if not isinstance(diccionario, dict):
        print("\n[ERROR] Estructura de datos no válida al mostrar parámetros.")
        return

    if "error" in diccionario:
        print("\n[ERROR] " + str(diccionario["error"]))
        return

    print("\n================ PARÁMETROS DE SANIDAD ================\n")

    # Función interna para mostrar un parámetro con sus campos.
    def imprimir_parametro(nombre, info):
        if isinstance(info, dict):
            print("- " + str(nombre) + ":")
            claves_info = list(info.keys())
            j = 0
            total_claves = len(claves_info)
            while j < total_claves:
                clave = claves_info[j]
                valor = info.get(clave)
                print("   - " + str(clave).capitalize() + ": " + str(valor))
                j = j + 1
            print("")

    # Caso general: se pidió todo el JSON (temperatura, humedad y calidad_aire)
    if "calidad_aire" in diccionario:
        temp = diccionario.get("temperatura")
        hum = diccionario.get("humedad")
        if temp is not None:
            imprimir_parametro("Temperatura", temp)
        if hum is not None:
            imprimir_parametro("Humedad", hum)

        calidad = diccionario.get("calidad_aire")
        if isinstance(calidad, dict):
            print("----- Calidad del Aire -----\n")
            claves_calidad = list(calidad.keys())
            i = 0
            total_param = len(claves_calidad)
            while i < total_param:
                clave_param = claves_calidad[i]
                info_param = calidad.get(clave_param)
                imprimir_parametro(clave_param, info_param)
                i = i + 1
    else:
        # Se pidió un parámetro concreto (temperatura, humedad o un gas/partícula)
        claves_dic = list(diccionario.keys())
        i = 0
        total = len(claves_dic)
        while i < total:
            clave = claves_dic[i]
            valor = diccionario.get(clave)
            imprimir_parametro(clave, valor)
            i = i + 1

    print("=======================================================\n")

def consultar_parametros_sanidad_interactivo():
    # Menú por consola para que el usuario consulte los parámetros de sanidad.

    print("\n=== CONSULTA DE PARÁMETROS DE SANIDAD ===")
    print("1. Ver todos los parámetros")
    print("2. Ver solo temperatura")
    print("3. Ver solo humedad")
    print("4. Ver un parámetro de calidad del aire (por nombre)")
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

def actualizar_parametro_sanidad(categoria, parametro, clave, nuevo_valor, ruta="valores_recomendados.json"):
    # Actualiza un valor en valores_recomendados.json.
    # categoria: "temperatura", "humedad" o "calidad_aire"
    # parametro: None para temperatura/humedad; nombre (ej: "PM2.5") para calidad_aire
    # clave: "min", "max", "unidad" o "descripcion"
    # nuevo_valor: valor nuevo que se quiere establecer

    datos = cargar_valores_recomendados_sanidad(ruta)
    if not datos:
        return False

    if categoria not in datos:
        print("\nLa categoría '" + str(categoria) + "' no existe en el JSON.")
        return False

    if categoria == "temperatura" or categoria == "humedad":
        if parametro is not None:
            print("\nPara temperatura/humedad no se utiliza un parámetro secundario.")
            return False

        bloque = datos.get(categoria)
        if not isinstance(bloque, dict):
            print("\nLa estructura de '" + str(categoria) + "' no es válida.")
            return False

        if clave not in bloque:
            print("\nLa clave '" + str(clave) + "' no existe en la categoría '" + str(categoria) + "'.")
            return False

        bloque[clave] = nuevo_valor

    elif categoria == "calidad_aire":
        calidad = datos.get("calidad_aire")
        if not isinstance(calidad, dict):
            print("\nLa sección 'calidad_aire' no es válida.")
            return False

        if parametro is None:
            print("\nDebe indicar el nombre del parámetro de calidad del aire (ej: PM2.5).")
            return False

        nombre_busqueda = parametro.strip().lower()
        claves_calidad = list(calidad.keys())
        i = 0
        total = len(claves_calidad)
        nombre_real = None

        # Búsqueda del parámetro en calidad_aire sin usar for
        while i < total and nombre_real is None:
            clave_actual = claves_calidad[i]
            if isinstance(clave_actual, str):
                if clave_actual.lower() == nombre_busqueda:
                    nombre_real = clave_actual
            i = i + 1

        if nombre_real is None:
            print("\nEl parámetro '" + str(parametro) + "' no existe en calidad_aire.")
            return False

        bloque_param = calidad.get(nombre_real)
        if not isinstance(bloque_param, dict):
            print("\nLa estructura del parámetro '" + str(nombre_real) + "' no es válida.")
            return False

        if clave not in bloque_param:
            print("\nLa clave '" + str(clave) + "' no existe en el parámetro '" + str(nombre_real) + "'.")
            return False

        bloque_param[clave] = nuevo_valor

    # Guardar cambios
    correcto = guardar_valores_recomendados_sanidad(datos, ruta)
    if correcto:
        print("\nParámetro actualizado correctamente.")
        return True
    else:
        return False


def cambiar_parametros_sanidad_interactivo():
    # Menú por consola para cambiar un parámetro de sanidad.

    print("\n=== CAMBIO DE PARÁMETROS DE SANIDAD ===")
    print("Categoría:")
    print("1. Temperatura")
    print("2. Humedad")
    print("3. Calidad del aire")
    opcion_cat = input("Selecciona la categoría: ").strip()

    categoria = None
    parametro = None

    if opcion_cat == "1":
        categoria = "temperatura"
    elif opcion_cat == "2":
        categoria = "humedad"
    elif opcion_cat == "3":
        categoria = "calidad_aire"
        parametro = input("Introduce el nombre del parámetro de calidad del aire (ej: PM2.5, CO2): ").strip()
    else:
        print("\nOpción de categoría no válida.")
        return

    print("\nClave a modificar:")
    print("1. min")
    print("2. max")
    print("3. unidad")
    print("4. descripcion")
    opcion_clave = input("Selecciona la clave: ").strip()

    clave = None
    if opcion_clave == "1":
        clave = "min"
    elif opcion_clave == "2":
        clave = "max"
    elif opcion_clave == "3":
        clave = "unidad"
    elif opcion_clave == "4":
        clave = "descripcion"
    else:
        print("\nOpción de clave no válida.")
        return

    # Pedimos el nuevo valor como texto.
    texto_valor = input("Introduce el nuevo valor para '" + clave + "': ").strip()

    # Intentamos convertir a número si la clave es min o max, manteniendo texto para unidad/descripcion.
    nuevo_valor = texto_valor
    if clave == "min" or clave == "max":
        try:
            # Intentamos convertir a número (float). Si el valor es entero, puede quedar como float igualmente.
            numero = float(texto_valor)
            nuevo_valor = numero
        except Exception:
            print("\nEl valor introducido para '" + clave + "' no es numérico. Se guardará como texto.")
            nuevo_valor = texto_valor

    actualizar_parametro_sanidad(categoria, parametro, clave, nuevo_valor)

