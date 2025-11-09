import json

# Nombre del archivo JSON con los usuarios
ARCHIVO_JSON = "usuarios.json"

def cargar_usuarios():
    """Carga la lista de usuarios desde el archivo JSON."""
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos["usuarios"]
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'usuarios.json'.")
        return []
    except json.JSONDecodeError:
        print("❌ Error: El archivo JSON tiene un formato incorrecto.")
        return []

def mostrar_usuarios(usuarios):
    """Muestra todos los usuarios cargados del archivo."""
    print("\n📋 Lista de usuarios registrados:")
    for u in usuarios:
        print(f"  ID: {u['id_usuario']:02d} | Usuario: {u['nombre_usuario']} | Nombre: {u['nombre']} {u['apellidos']}")

def comprobar_login(usuarios, nombre_usuario, contraseña):
    """Verifica si el usuario y la contraseña coinciden."""
    for u in usuarios:
        if u["nombre_usuario"] == nombre_usuario and u["contraseña"] == contraseña:
            return u
    return None

def main():
    usuarios = cargar_usuarios()
    if not usuarios:
        return

    mostrar_usuarios(usuarios)

    print("\n🔐 Prueba de inicio de sesión:")
    nombre_usuario = input("Introduce el nombre de usuario: ")
    contraseña = input("Introduce la contraseña: ")

    usuario = comprobar_login(usuarios, nombre_usuario, contraseña)
    if usuario:
        print(f"\n✅ Inicio de sesión correcto. Bienvenido/a {usuario['nombre']} {usuario['apellidos']}.\n")
    else:
        print("\n❌ Usuario o contraseña incorrectos. Inténtalo de nuevo.\n")

if __name__ == "__main__":
    main()
