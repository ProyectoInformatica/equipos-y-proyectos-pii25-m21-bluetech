from modeloBlueTech import RepositorioCredenciales

def main():
    repo = RepositorioCredenciales("admins.json", "usuarios.json")
    print("=== Login BlueTech (sin hash) ===")
    username = input("Usuario: ").strip()
    contrasena = input("Contraseña: ").strip()

    u = repo.verificar_login(username, contrasena)
    if u is None:
        print("\nCredenciales incorrectas.")
    else:
        print("\nBienvenido/a,", u.nombre_mostrado)
        print("Rol:", u.rol.value)

if __name__ == "__main__":
    main()
