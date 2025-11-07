from modeloBlueTech import RepositorioCredenciales, Rol


def mostrar_menu_principal():
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Iniciar sesión")
    print("2. Salir")
    return input("Selecciona una opción: ").strip()


def seleccionar_rol():
    print("\n=== SELECCIÓN DE ROL ===")
    print("1. Administrador")
    print("2. Trabajador")
    opcion = input("Selecciona tu rol: ").strip()

    if opcion == "1":
        return Rol.ADMINISTRADOR
    elif opcion == "2":
        return Rol.TRABAJADOR
    else:
        print("Opción no válida. Intenta de nuevo.")
        return None


def mostrar_menu_admin(usuario):
    sesion_activa = True
    while sesion_activa:
        print("\n=== MENÚ ADMINISTRADOR ===")
        print("Usuario:", usuario.nombre_usuario)
        print("1. Ver usuarios del sistema (simulado)")
        print("2. Configurar parámetros (simulado)")
        print("3. Cerrar sesión")
        eleccion = input("Selecciona una opción: ").strip()

        if eleccion == "1":
            print("Listado de usuarios (demo).")
        elif eleccion == "2":
            print("Configuración de parámetros (demo).")
        elif eleccion == "3":
            sesion_activa = False
        else:
            print("Opción no válida.")


def mostrar_menu_trabajador(usuario):
    sesion_activa = True
    while sesion_activa:
        print("\n=== MENÚ TRABAJADOR ===")
        print("Usuario:", usuario.nombre_usuario)
        print("1. Consultar estado de salas (simulado)")
        print("2. Ver parámetros ambientales (simulado)")
        print("3. Cerrar sesión")
        eleccion = input("Selecciona una opción: ").strip()

        if eleccion == "1":
            print("Consultando salas (demo).")
        elif eleccion == "2":
            print("Mostrando parámetros ambientales (demo).")
        elif eleccion == "3":
            sesion_activa = False
        else:
            print("Opción no válida.")


def main():
    print("=======================================")
    print("   Bienvenido/a al sistema BlueTech")
    print("=======================================")

    repo = RepositorioCredenciales("admins.json", "usuarios.json")
    ejecutando = True

    while ejecutando:
        opcion = mostrar_menu_principal()

        if opcion == "1":
            rol = None
            while rol is None:
                rol = seleccionar_rol()

            usuario_valido = None
            while usuario_valido is None:
                nombre_usuario = input("Usuario: ").strip()
                contrasena = input("Contraseña: ").strip()

                usuario_valido = repo.verificar_login(nombre_usuario, contrasena, rol)

                if usuario_valido is None:
                    print("\nCredenciales incorrectas. Vuelve a intentarlo.\n")

            print("\nBienvenido/a,", usuario_valido.nombre_usuario)

            if usuario_valido.es_administrador():
                mostrar_menu_admin(usuario_valido)
            elif usuario_valido.es_trabajador():
                mostrar_menu_trabajador(usuario_valido)

        elif opcion == "2":
            print("\nSaliendo del sistema. Hasta pronto.")
            ejecutando = False
        else:
            print("\nOpción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()
