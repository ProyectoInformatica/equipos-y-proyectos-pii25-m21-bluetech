# view/gestion_usuarios_view.py
import hashlib
import flet as ft
from controller.gestion_usuarios_controller import GestionUsuariosController

BASE_ID_TRABAJADOR = 1001
BASE_ID_ADMIN = 2001


def mostrar_pantalla_gestion_usuarios(page: ft.Page, usuario, repo, on_volver):
    page.controls.clear()
    page.scroll = None
    page.padding = 0
    page.spacing = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = None

    controller = GestionUsuariosController()

    confirm_add = {"active": False, "data": None}
    confirm_del = {"active": False, "id": None}

    msg_add = ft.Text("", size=14, weight="bold", text_align="center")
    msg_del = ft.Text("", size=14, weight="bold", text_align="center")

    # =================== CONTROLES ===================
    W_LEFT = 420
    W_HALF = 205

    campo_nombre = ft.TextField(label="Nombre", width=W_HALF)
    campo_apellidos = ft.TextField(label="Apellidos", width=W_HALF)
    campo_login = ft.TextField(label="Usuario (login)", width=W_HALF)
    campo_pass = ft.TextField(label="Contraseña temporal", password=True, can_reveal_password=True, width=W_HALF)

    dropdown_rol = ft.Dropdown(
        label="Rol",
        width=W_LEFT,
        value="trabajador",
        options=[ft.dropdown.Option("trabajador"), ft.dropdown.Option("administrador")],
    )

    btn_add = ft.ElevatedButton(
        "Añadir usuario",
        icon=ft.Icons.PERSON_ADD,
        bgcolor="#1565c0",
        color="white",
        width=W_LEFT,
        height=52,
    )

    campo_id = ft.TextField(
        label="ID del usuario a eliminar",
        width=W_LEFT,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align="center",
    )

    btn_del = ft.ElevatedButton(
        "Eliminar usuario",
        icon=ft.Icons.DELETE_FOREVER,
        bgcolor="#d32f2f",
        color="white",
        width=W_LEFT,
        height=52,
    )

    btn_volver = ft.ElevatedButton(
        "Volver al menú",
        icon=ft.Icons.ARROW_BACK_IOS_NEW,
        bgcolor="#1565c0",
        color="white",
        width=150,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            text_style=ft.TextStyle(size=13, weight="w600"),
        ),
    )

    # =================== LISTADOS ===================
    listado_trab = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4)
    listado_admin = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4)

    cont_listado_trab = ft.Container(
        content=listado_trab,
        bgcolor="#f8fbff",
        padding=16,
        border_radius=15,
        border=ft.border.all(1, "#bbdefb"),
        width=520,
        expand=2,
    )

    cont_listado_admin = ft.Container(
        content=listado_admin,
        bgcolor="#fff7f7",
        padding=16,
        border_radius=15,
        border=ft.border.all(1, "#ffcdd2"),
        width=520,
        expand=1,
    )

    AVISO_MIGRACION = "⚠️ IDs sin migrar. Actualiza usuarios.json a trabajadores 1001+ y admins 2001+."

    # =================== REFRESCAR ===================
    def refrescar():
        ok, aviso = controller.comprobar_migracion()
        if not ok:
            msg_del.value = aviso
            msg_del.color = "orange"
        else:
            if (msg_del.value or "").startswith("⚠️"):
                msg_del.value = ""

        listado_trab.controls.clear()
        listado_admin.controls.clear()

        trabajadores, admins = controller.obtener_listados()

        if not trabajadores:
            listado_trab.controls.append(ft.Text("No hay trabajadores registrados.", color="grey", italic=True))
        else:
            for u in trabajadores:
                listado_trab.controls.append(
                    ft.Text(f"ID: {u['id']} → {u['login']} (Trabajador)", size=14, color="#1565c0")
                )

        if not admins:
            listado_admin.controls.append(ft.Text("No hay administradores registrados.", color="grey", italic=True))
        else:
            for u in admins:
                listado_admin.controls.append(
                    ft.Text(f"ID: {u['id']} → {u['login']} (Administrador)", size=14, color="#d32f2f", weight="bold")
                )

        page.update()

    # =================== AÑADIR ===================
    def añadir(e):
        msg_add.value = ""
        ok, _ = controller.comprobar_migracion()
        if not ok:
            msg_add.value = "⚠️ Acción bloqueada hasta migrar usuarios.json."
            msg_add.color = "orange"
            page.update()
            return

        if not all([campo_nombre.value, campo_apellidos.value, campo_login.value, campo_pass.value]):
            msg_add.value = "Todos los campos son obligatorios."
            msg_add.color = "red"
            page.update()
            return

        login = campo_login.value.strip()
        rol = (dropdown_rol.value or "").lower()

        payload = {
            "nombre": campo_nombre.value.strip(),
            "apellidos": campo_apellidos.value.strip(),
            "login": login,
            "rol": rol,
            "hash": hashlib.sha256(campo_pass.value.encode("utf-8")).hexdigest(),
        }

        if not confirm_add["active"] or confirm_add["data"] != payload:
            confirm_add["active"] = True
            confirm_add["data"] = payload
            msg_add.value = f"¿Crear usuario '{login}' ({rol})? Pulsa otra vez para confirmar."
            msg_add.color = "orange"
            page.update()
            return

        ok, msg = controller.crear_usuario(payload)
        msg_add.value = f"Usuario '{login}' creado correctamente (ID: {msg})" if ok else msg
        msg_add.color = "#2e7d32" if ok else "red"
        confirm_add["active"] = False
        confirm_add["data"] = None
        msg_add.value = f"Usuario '{login}' creado correctamente (ID: {msg})" if ok else msg
        msg_add.color = "#2e7d32" if ok else "red"

        for c in [campo_nombre, campo_apellidos, campo_login, campo_pass]:
            c.value = ""
        dropdown_rol.value = "trabajador"

        refrescar()
        page.update()

    # =================== ELIMINAR ===================
    def eliminar(e):
        msg_add.value = ""
        ok, _ = controller.comprobar_migracion()
        if not ok:
            page.update()
            return

        raw = (campo_id.value or "").strip()
        if not raw.isdigit():
            msg_del.value = "Introduce un ID numérico válido."
            msg_del.color = "red"
            page.update()
            return

        id_elim = int(raw)
        if hasattr(usuario, "id_usuario") and usuario.id_usuario == id_elim:
            msg_del.value = "No puedes eliminar tu propio usuario."
            msg_del.color = "red"
            confirm_del["active"] = False
            confirm_del["id"] = None
            page.update()
            return

        if not confirm_del["active"] or confirm_del["id"] != id_elim:
            confirm_del["active"] = True
            confirm_del["id"] = id_elim
            msg_del.value = f"¿Eliminar usuario ID {id_elim}? Pulsa otra vez para confirmar."
            msg_del.color = "orange"
            page.update()
            return

        ok, msg = controller.eliminar_usuario(id_elim)
        confirm_del["active"] = False
        confirm_del["id"] = None
        msg_del.value = msg if msg else f"Usuario ID {id_elim} eliminado correctamente."
        msg_del.color = "#2e7d32" if ok else "red"

        campo_id.value = ""
        refrescar()
        page.update()

    # =================== EVENTOS ===================
    btn_add.on_click = añadir
    btn_del.on_click = eliminar
    btn_volver.on_click = lambda e: on_volver()

    # =================== LAYOUT ===================
    bloque_añadir = ft.Column(
        [
            ft.Text("Añadir usuario", weight="bold", size=20, color="#1565c0"),
            ft.Row([campo_nombre, campo_apellidos], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([campo_login, campo_pass], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            dropdown_rol,
            btn_add,
            msg_add,
        ],
        spacing=10,
    )

    bloque_eliminar = ft.Column(
        [
            ft.Text("Eliminar usuario", weight="bold", size=20, color="#d32f2f"),
            campo_id,
            btn_del,
            msg_del,
        ],
        spacing=10,
    )

    panel_izquierdo = ft.Container(
        width=W_LEFT,
        content=ft.Column(
            [
                bloque_añadir,
                ft.Divider(height=1, color="#e0e0e0"),
                bloque_eliminar,
            ],
            spacing=18,
        ),
    )

    panel_derecho = ft.Container(
        expand=True,
        content=ft.Column(
            [
                cont_listado_trab,
                ft.Container(height=16),
                cont_listado_admin,
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    cuerpo = ft.Row(
        [
            panel_izquierdo,
            ft.Container(width=35),
            panel_derecho,
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True,
    )

    tarjeta_blanca = ft.Container(
        width=1120,
        height=700,
        padding=35,
        bgcolor="white",
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, color="#30000000"),
        content=ft.Column(
            [
                ft.Row([btn_volver], alignment=ft.MainAxisAlignment.START),
                ft.Text(
                    "Gestión de usuarios - Administrador",
                    size=30,
                    weight="bold",
                    color="#1565c0",
                    text_align="center",
                ),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.Container(expand=True, content=cuerpo),
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )

    page.add(
        ft.Stack(
            [
                ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
                ft.Container(expand=True, alignment=ft.alignment.center, content=tarjeta_blanca),
            ],
            expand=True,
        )
    )

    refrescar()
