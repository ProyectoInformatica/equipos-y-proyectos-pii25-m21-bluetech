# Se importan las clases necesarias desde el módulo de modelo.
# RepositorioCredenciales: maneja la carga, verificación y eliminación de usuarios.
# Rol: define los posibles roles de los usuarios (administrador y trabajador).
from modeloBlueTech import RepositorioCredenciales, Rol


# Muestra el menú principal del programa y devuelve la opción seleccionada.
def mostrar_menu_principal():
    # Muestra las opciones principales de la aplicación.
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Iniciar sesión")
    print("2. Salir")

    # Se devuelve la opción elegida por el usuario, eliminando espacios en blanco.
    return input("Selecciona una opción: ").strip()


# Permite al usuario seleccionar el rol con el que quiere iniciar sesión.
def seleccionar_rol():
    # Muestra el submenú de selección de rol.
    print("\n=== SELECCIÓN DE ROL ===")
    print("1. Administrador")
    print("2. Trabajador")

    opcion = input("Selecciona tu rol: ").strip()

    # Dependiendo de la opción, se devuelve el rol correspondiente.
    if opcion == "1":
        return Rol.ADMINISTRADOR
    if opcion == "2":
        return Rol.TRABAJADOR

    # Si no se selecciona una opción válida, se informa y se devuelve None.
    print("Opción no válida. Intenta de nuevo.")
    return None


# Menú para usuarios con rol ADMINISTRADOR.
# Recibe:
#   - usuario: objeto Usuario autenticado.
#   - repo:    instancia de RepositorioCredenciales para acceder a usuarios y JSON.
def mostrar_menu_admin(usuario, repo):
    # Bandera para controlar la sesión dentro del menú de administrador.
    sesion_activa = True

    while sesion_activa:
        print("\n=== MENÚ ADMINISTRADOR ===")
        print("Usuario autenticado:", usuario.nombre_usuario)
        print("1. Listar todos los usuarios")
        print("2. Buscar usuario por nombre de login")
        print("3. Eliminar usuario por ID")
        print("0. Cerrar sesión")

        eleccion = input("Selecciona una opción: ").strip()

        # Opción 1: mostrar todos los usuarios cargados en el repositorio.
        if eleccion == "1":
            print("\n--- LISTADO DE USUARIOS ---")
            i = 0
            total = len(repo.usuarios)
            while i < total:
                u = repo.usuarios[i]
                # Se muestra el ID, el nombre de login y el rol (valor legible del Enum).
                print(
                    "ID:", u.id_usuario,
                    "| Usuario (login):", u.nombre_usuario,
                    "| Rol:", u.rol
                )
                i = i + 1

        # Opción 2: buscar un usuario concreto por su nombre de login.
        elif eleccion == "2":
            nombre_busqueda = input("Introduce el nombre de usuario a buscar: ").strip()
            encontrado = None

            i = 0
            total = len(repo.usuarios)
            while i < total and encontrado is None:
                u = repo.usuarios[i]
                if u.nombre_usuario == nombre_busqueda:
                    encontrado = u
                else:
                    i = i + 1

            if encontrado is None:
                print("No se ha encontrado ningún usuario con ese nombre de login.")
            else:
                print("Usuario encontrado:")
                print(
                    "ID:", encontrado.id_usuario,
                    "| Usuario (login):", encontrado.nombre_usuario,
                    "| Rol:", encontrado.rol    
                )

        # Opción 3: eliminar un usuario por ID con confirmación.
        elif eleccion == "3":
            id_texto = input("Introduce el ID del usuario a eliminar: ").strip()
            if id_texto.isdigit():
                id_eliminar = int(id_texto)
                # Se delega la lógica de búsqueda, confirmación y borrado en el repositorio.
                repo.eliminar_usuario_por_id(id_eliminar)
            else:
                print("El ID debe ser un número entero.")

        # Opción 0: fin de sesión.
        elif eleccion == "0":
            sesion_activa = False
            print("Cerrando sesión de administrador...")

        # Cualquier otra cosa: opción no válida.
        else:
            print("Opción no válida.")


# Muestra el menú de opciones para un usuario con rol de trabajador.
# Recibe:
#   - usuario: objeto Usuario autenticado como trabajador.
def mostrar_menu_trabajador(usuario):
    # Bandera para controlar la sesión dentro del menú de trabajador.
    sesion_activa = True

    while sesion_activa:
        print("\n=== MENÚ TRABAJADOR ===")
        print("Usuario autenticado:", usuario.nombre_usuario)
        print("1. Consultar estado de salas (simulado)")
        print("2. Ver parámetros ambientales (simulado)")
        print("0. Cerrar sesión")

        eleccion = input("Selecciona una opción: ").strip()

        # Opción 1: funcionalidad simulada de consulta de salas.
        if eleccion == "1":
            print("\nConsultando estado de salas (demo).")

        # Opción 2: funcionalidad simulada de parámetros ambientales.
        elif eleccion == "2":
            print("\nMostrando parámetros ambientales (demo).")

        # Opción 0: cerrar sesión del trabajador.
        elif eleccion == "0":
            sesion_activa = False

        # Cualquier otra opción se considera inválida.
        else:
            print("\nOpción no válida. Intente de nuevo.")


# Punto de entrada principal del programa.
def main():
    # Mensaje de bienvenida al sistema.
    print("=======================================")
    print("   Bienvenido/a al sistema BlueTech")
    print("=======================================")

    # Se crea el repositorio de credenciales indicando la ruta del archivo JSON
    # que contiene todos los usuarios (administradores y trabajadores).
    # Si en tu modelo el constructor de RepositorioCredenciales solo recibe ruta_usuarios,
    # esta llamada es compatible porque se usa el parámetro con nombre.
    repo = RepositorioCredenciales(ruta_usuarios="usuarios.json")

    # Bandera que controla el ciclo principal del programa.
    ejecutando = True

    while ejecutando:
        # Se muestra el menú principal y se obtiene la opción seleccionada.
        opcion = mostrar_menu_principal()

        if opcion == "1":
            # El usuario debe seleccionar el rol con el que quiere iniciar sesión.
            rol_seleccionado = None
            while rol_seleccionado is None:
                rol_seleccionado = seleccionar_rol()

            # Variable donde se almacenará el usuario autenticado.
            usuario_valido = None

            # Se repite el proceso de login hasta que se introduzcan credenciales correctas.
            while usuario_valido is None:
                nombre_usuario = input("Usuario: ").strip()
                contrasena = input("Contraseña: ").strip()

                # Se verifica el login contra el repositorio de credenciales.
                usuario_valido = repo.verificar_login(
                    nombre_usuario,
                    contrasena,
                    rol_seleccionado
                )

                if usuario_valido is None:
                    print("\nCredenciales incorrectas. Vuelve a intentarlo.\n")

            # En este punto, el usuario se ha autenticado correctamente.
            print("\nBienvenido/a,", usuario_valido.nombre_usuario)

            # Dependiendo del rol del usuario autenticado, se muestra el menú adecuado.
            if usuario_valido.es_administrador():
                mostrar_menu_admin(usuario_valido, repo)
            elif usuario_valido.es_trabajador():
                mostrar_menu_trabajador(usuario_valido)

        elif opcion == "2":
            # El usuario elige salir de la aplicación.
            print("\nSaliendo del sistema. Hasta pronto.")
            ejecutando = False

        else:
            # Opción inválida en el menú principal.
            print("\nOpción no válida. Intente de nuevo.")


# Este bloque se ejecuta solo si el archivo se ejecuta directamente,
# no cuando se importa como módulo desde otro archivo.
if __name__ == "__main__":
    main()
