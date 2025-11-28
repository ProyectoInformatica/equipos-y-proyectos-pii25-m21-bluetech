# vista/gestion_usuarios_view.py
import json
import hashlib
import flet as ft
from modeloBlueTech import RepositorioCredenciales


def mostrar_pantalla_gestion_usuarios(page: ft.Page, usuario, repo: RepositorioCredenciales, on_volver):
    page.controls.clear()

    confirm_add = {"active": False, "data": None}
    confirm_del = {"active": False, "id": None}

    # Mensajes locales para cada sección
    msg_add = ft.Text("", size=15, weight="bold", text_align="center")
    msg_del = ft.Text("", size=15, weight="bold", text_align="center")

    # === AÑADIR USUARIO ===
    campo_nombre = ft.TextField(label="Nombre", width=380)
    campo_apellidos = ft.TextField(label="Apellidos", width=380)
    campo_login = ft.TextField(label="Usuario (login)", width=380)
    campo_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=380)
    dropdown_rol = ft.Dropdown(
        label="Rol",
        width=380,
        value="trabajador",
        options=[ft.dropdown.Option("trabajador"), ft.dropdown.Option("administrador")]
    )
    btn_add = ft.ElevatedButton(
        "Añadir usuario",
        icon=ft.Icons.PERSON_ADD,
        bgcolor="#1565c0",
        color="white",
        width=380,
        height=52
    )

    # === ELIMINAR USUARIO ===
    campo_id = ft.TextField(
        label="ID del usuario a eliminar",
        width=320,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align="center"
    )
    btn_del = ft.ElevatedButton(
        "Eliminar usuario",
        icon=ft.Icons.DELETE_FOREVER,
        bgcolor="#d32f2f",
        color="white",
        width=320,
        height=52
    )

    # === LISTADO ===
    listado = ft.Column(scroll=ft.ScrollMode.AUTO, height=380)
    cont_listado = ft.Container(
        content=listado,
        bgcolor="#f8fbff",
        padding=20,
        border_radius=15,
        border=ft.border.all(1, "#bbdefb")
    )

    btn_volver = ft.ElevatedButton(
        "Volver al menú",
        icon=ft.Icons.ARROW_BACK_IOS_NEW,
        bgcolor="#1565c0",
        color="white",
        width=380,
        height=55
    )

    def refrescar():
        repo.cargar_datos()
        listado.controls.clear()
        if not repo.usuarios:
            listado.controls.append(ft.Text("No hay usuarios registrados", color="gray", italic=True, text_align="center"))
        else:
            for u in repo.usuarios:
                rol = "Administrador" if u.rol == "administrador" else "Trabajador"
                color = "#d32f2f" if u.rol == "administrador" else "#1565c0"
                listado.controls.append(
                    ft.Text(f"ID: {u.id_usuario} → {u.nombre_usuario} ({rol})", size=14, weight="bold" if u.rol == "administrador" else "normal", color=color)
                )
        page.update()

    # =================== AÑADIR ===================
    def añadir(e):
        msg_add.value = ""
        msg_del.value = ""

        if not all([campo_nombre.value, campo_apellidos.value, campo_login.value, campo_pass.value]):
            msg_add.value = "Todos los campos son obligatorios"
            msg_add.color = "red"
            page.update()
            return

        login = campo_login.value.strip()
        if any(u.nombre_usuario == login for u in repo.usuarios):
            msg_add.value = "El usuario ya existe"
            msg_add.color = "red"
            page.update()
            return

        if not confirm_add["active"]:
            confirm_add["active"] = True
            confirm_add["data"] = {
                "nombre": campo_nombre.value.strip(),
                "apellidos": campo_apellidos.value.strip(),
                "nombre_usuario": login,
                "contrasena_hash": hashlib.sha256(campo_pass.value.encode()).hexdigest(),
                "rol": dropdown_rol.value
            }
            msg_add.value = f"¿Crear usuario '{login}'? Pulsa otra vez"
            msg_add.color = "orange"
            page.update()
            return

        # Guardar en JSON
        try:
            with open("usuarios.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            nuevo_id = max((u.get("id_usuario", 0) for u in data["usuarios"]), default=0) + 1
            nuevo = confirm_add["data"].copy()
            nuevo["id_usuario"] = nuevo_id
            data["usuarios"].append(nuevo)
            with open("usuarios.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            for c in [campo_nombre, campo_apellidos, campo_login, campo_pass]:
                c.value = ""
            confirm_add["active"] = False
            msg_add.value = f"Usuario '{login}' creado (ID: {nuevo_id})"
            msg_add.color = "green500"
            refrescar()
        except Exception as ex:
            msg_add.value = f"Error: {ex}"
            msg_add.color = "red"
        page.update()

    # =================== ELIMINAR ===================
    def eliminar(e):
        msg_add.value = ""
        msg_del.value = ""

        # Validar ID
        if not campo_id.value or not campo_id.value.isdigit():
            msg_del.value = "ID no válido"
            msg_del.color = "red"
            page.update()
            return

        id_elim = int(campo_id.value)

        # Buscar SOLO un usuario TRABAJADOR con ese ID en repo.usuarios
        usuario_trabajador = next(
            (
                u for u in repo.usuarios
                if u.id_usuario == id_elim and (u.rol or "").lower() == "trabajador"
            ),
            None,
        )

        if usuario_trabajador is None:
            # No hay trabajador con ese ID (o es admin)
            msg_del.value = (
                "No existe ningún usuario con ese ID y rol 'trabajador' "
                "(o el usuario es administrador)."
            )
            msg_del.color = "red"
            page.update()
            return

        # Confirmación en dos pasos
        if not confirm_del["active"] or confirm_del["id"] != id_elim:
            confirm_del["active"] = True
            confirm_del["id"] = id_elim
            msg_del.value = (
                f"¿Eliminar usuario ID {id_elim}? Pulsa otra vez "
                "(solo se eliminarán usuarios con rol 'trabajador')."
            )
            msg_del.color = "orange"
            page.update()
            return

        # Segundo clic: eliminar del JSON SOLO al trabajador
        try:
            with open("usuarios.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            usuarios_json = data.get("usuarios", [])
            nueva_lista = []

            for u in usuarios_json:
                mismo_id = u.get("id_usuario") == id_elim
                rol_json = (u.get("rol") or "").lower()
                # Conservamos admins u otros roles aunque compartan ID
                if not (mismo_id and rol_json == "trabajador"):
                    nueva_lista.append(u)

            data["usuarios"] = nueva_lista

            with open("usuarios.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            campo_id.value = ""
            confirm_del["active"] = False
            msg_del.value = f"Usuario ID {id_elim} eliminado"
            msg_del.color = "green500"
            refrescar()
        except Exception as ex:
            msg_del.value = f"Error: {ex}"
            msg_del.color = "red"

        page.update()

    # =================== EVENTOS ===================
    btn_add.on_click = añadir
    btn_del.on_click = eliminar
    btn_volver.on_click = lambda e: on_volver()

    # =================== LAYOUT FINAL ===================
    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),

            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Container(
                    width=1000,
                    padding=50,
                    bgcolor="white",
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=30, color="#30000000"),
                    content=ft.Column([
                        ft.Text("Gestión de usuarios - Administrador", size=32, weight="bold", color="#1565c0", text_align="center"),
                        ft.Text(f"Conectado como: {usuario.nombre_usuario}", color="#555", size=15, italic=True),
                        ft.Divider(height=1, color="#e0e0e0"),

                        ft.Text("Añadir nuevo usuario", weight="bold", size=22, color="#1565c0"),
                        campo_nombre, campo_apellidos, campo_login, campo_pass, dropdown_rol,
                        ft.Container(height=12),
                        btn_add,
                        msg_add,                                 # Mensaje justo debajo del botón

                        ft.Divider(height=1, color="#e0e0e0", thickness=0.8),

                        ft.Text("Eliminar usuario por ID", weight="bold", size=22, color="#d32f2f"),
                        ft.Container(height=15),
                        campo_id,
                        ft.Container(height=12),
                        btn_del,
                        msg_del,                                 # Mensaje justo debajo del botón rojo

                        ft.Divider(height=1, color="#e0e0e0", thickness=0.8),

                        ft.Text("Listado de usuarios registrados:", weight="bold", size=18, color="#1565c0"),
                        cont_listado,

                        ft.Container(height=30),
                        btn_volver
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment="center",
                    spacing=20)
                )
            )
        ], expand=True)
    )

    refrescar()
