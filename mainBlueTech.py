# Se importan las clases necesarias 
# RepositorioCredenciales: maneja usuarios y contraseñas
# Rol: define los roles de usuario (administrador o trabajador)
from modeloBlueTech import RepositorioCredenciales, Rol


# Muestra el menú principal del programa y devuelve la opción seleccionada por el usuario.
def mostrar_menu_principal():
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Iniciar sesión")
    print("2. Salir")
    # Se devuelve la opción elegida (sin espacios en blanco).
    return input("Selecciona una opción: ").strip()


# Permite al usuario elegir si quiere iniciar sesión como administrador o trabajador.
def seleccionar_rol():
    print("\n=== SELECCIÓN DE ROL ===")
    print("1. Administrador")
    print("2. Trabajador")
    opcion = input("Selecciona tu rol: ").strip()

    # Dependiendo de la opción ingresada, se devuelve el rol correspondiente.
    if opcion == "1":
        return Rol.ADMINISTRADOR
    elif opcion == "2":
        return Rol.TRABAJADOR
    else:
        # Si la opción no es válida, se muestra un mensaje y devuelve None.
        print("Opción no válida. Intenta de nuevo.")
        return None


# Muestra las opciones disponibles para un usuario con rol de administrador.
# Recibe como parámetro el objeto 'usuario' autenticado.
def mostrar_menu_admin(usuario):
    sesion_activa = True  # Bandera que controla la sesión del usuario.
    while sesion_activa:
        print("\n=== MENÚ ADMINISTRADOR ===")
        print("Usuario:", usuario.nombre_usuario)
        print("1. Ver usuarios del sistema (simulado)")
        print("2. Configurar parámetros (simulado)")
        print("3. Cerrar sesión")
        eleccion = input("Selecciona una opción: ").strip()

        # Opciones de demostración (no realizan acciones reales).
        if eleccion == "1":
            print("Listado de usuarios (demo).")
        elif eleccion == "2":
            print("Configuración de parámetros (demo).")
        elif eleccion == "3":
            sesion_activa = False  # Finaliza la sesión.
        else:
            print("Opción no válida.")

# Muestra las opciones para un usuario con rol de trabajador.
# Recibe como parámetro el objeto 'usuario' autenticado.
def mostrar_menu_trabajador(usuario):
    sesion_activa = True
    while sesion_activa:
        print("\n=== MENÚ TRABAJADOR ===")
        print("Usuario:", usuario.nombre_usuario)
        print("1. Consultar estado de salas (simulado)")
        print("2. Ver parámetros ambientales (simulado)")
        print("3. Cerrar sesión")
        eleccion = input("Selecciona una opción: ").strip()

        # Opciones de demostración (sin funcionalidad real).
        if eleccion == "1":
            print("Consultando salas (demo).")
        elif eleccion == "2":
            print("Mostrando parámetros ambientales (demo).")
        elif eleccion == "3":
            sesion_activa = False  # Finaliza la sesión.
        else:
            print("Opción no válida.")


# Es el punto de entrada del programa. Controla el flujo principal del sistema.
def main():
    # Mensaje de bienvenida
    print("=======================================")
    print("   Bienvenido/a al sistema BlueTech")
    print("=======================================")

    # Se crea un repositorio de credenciales con las rutas a los archivos JSON.
    repo = RepositorioCredenciales("admins.json", "usuarios.json")

    ejecutando = True  # Controla el ciclo principal del programa.

    while ejecutando:
        # Se muestra el menú principal y se obtiene la opción seleccionada.
        opcion = mostrar_menu_principal()

        if opcion == "1":
            rol = None
            # El usuario debe seleccionar un rol válido.
            while rol is None:
                rol = seleccionar_rol()

            usuario_valido = None
            # Pide credenciales hasta que el usuario se autentique correctamente.
            while usuario_valido is None:
                nombre_usuario = input("Usuario: ").strip()
                contrasena = input("Contraseña: ").strip()

                # Se verifica si las credenciales existen en el repositorio.
                usuario_valido = repo.verificar_login(nombre_usuario, contrasena, rol)

                # Si no se encontró, se muestra un mensaje y se repite.
                if usuario_valido is None:
                    print("\nCredenciales incorrectas. Vuelve a intentarlo.\n")

            # Si se logra autenticar, se da la bienvenida.
            print("\nBienvenido/a,", usuario_valido.nombre_usuario)

            # Dependiendo del rol del usuario, se muestra el menú correspondiente.
            if usuario_valido.es_administrador():
                mostrar_menu_admin(usuario_valido)
            elif usuario_valido.es_trabajador():
                mostrar_menu_trabajador(usuario_valido)

        elif opcion == "2":
            print("\nSaliendo del sistema. Hasta pronto.")
            ejecutando = False  # Finaliza el bucle principal.

        else:
            print("\nOpción no válida. Intente de nuevo.")


# Este bloque se ejecuta solo si el script se ejecuta directamente (no al importarse como módulo).
if __name__ == "__main__":
    main()
