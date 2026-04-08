import hashlib
import flet as ft
from controller.gestion_usuarios_controller import GestionUsuariosController

def mostrar_pantalla_gestion_usuarios(page: ft.Page, usuario, repo, on_volver):
    page.controls.clear()
    page.padding = 0
    page.bgcolor = ft.Colors.BLUE_GREY_50

    controller = GestionUsuariosController()

    confirm_add = {"active": False, "data": None}
    confirm_del = {"active": False, "id": None}

    msg_add = ft.Text("", size=13, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    msg_del = ft.Text("", size=13, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    #Ajuste de anchos para que quepan 3 columnas de lista
    W_LEFT = 350 
    W_HALF = 170

    #--- DISEÑO ---
    def crear_input(label, icon, width=W_LEFT, password=False):
        return ft.TextField(
            label=label,
            width=width,
            prefix_icon=icon,
            password=password,
            can_reveal_password=password,
            border_radius=10,
            bgcolor=ft.Colors.GREY_50,
            text_size=14
        )

    def crear_contenedor_lista(titulo, color, icon, control_lista):
        return ft.Container(
            expand=True,
            padding=15,
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=color, size=20), ft.Text(titulo, weight=ft.FontWeight.BOLD, color=color)]),
                ft.Divider(height=10),
                control_lista
            ])
        )

    #--- CONTROLES UI ---
    campo_nombre = crear_input("Nombre", ft.Icons.PERSON_OUTLINE, width=W_HALF)
    campo_apellidos = crear_input("Apellidos", ft.Icons.PERSON_OUTLINE, width=W_HALF)
    campo_login = crear_input("Usuario (Login)", ft.Icons.ACCOUNT_CIRCLE_OUTLINED, width=W_HALF)
    campo_pass = crear_input("Pass Temporal", ft.Icons.PASSWORD, width=W_HALF, password=True)

    dropdown_rol = ft.Dropdown(
        label="Rol del Sistema",
        width=W_LEFT,
        border_radius=10,
        value="trabajador",
        options=[
            ft.dropdown.Option("trabajador", "Trabajador (Técnico Base)"),
            ft.dropdown.Option("tecnico", "Técnico (Especialista)"),
            ft.dropdown.Option("administrador", "Administrador (Control)")
        ],
    )

    campo_id_del = crear_input("ID numérico a eliminar", ft.Icons.DELETE_OUTLINE)
    campo_id_del.text_align = ft.TextAlign.CENTER

    listado_trab = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=8)
    listado_tecn = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=8)
    listado_admin = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=8)

    #--- LÓGICA DE REFRESCADO ---
    def refrescar():
        ok_mig, aviso = controller.comprobar_migracion()
        if not ok_mig:
            msg_del.value = aviso
            msg_del.color = ft.Colors.ORANGE_800
        else:
            msg_del.value = ""

        listado_trab.controls.clear()
        listado_tecn.controls.clear()
        listado_admin.controls.clear()

        data = controller.model.leer()
        usuarios = data.get("usuarios", [])

        trabajadores = []
        tecnicos = []
        administradores = []

        for u in usuarios:
            rol = u.get("rol")
            user_data = {
                "id": u.get("id_usuario"),
                "login": u.get("nombre_usuario")
            }

            if rol == "trabajador":
                trabajadores.append(user_data)
            elif rol == "tecnico":
                tecnicos.append(user_data)
            elif rol == "administrador":
                administradores.append(user_data)

        #Ordenar
        trabajadores.sort(key=lambda x: x["id"])
        tecnicos.sort(key=lambda x: x["id"])
        administradores.sort(key=lambda x: x["id"])

        #Trabajadores
        if not trabajadores:
            listado_trab.controls.append(ft.Text("Sin trabajadores", color="grey"))
        else:
            for u in trabajadores:
                listado_trab.controls.append(
                    ft.Text(f"ID: {u['id']} - {u['login']}", color=ft.Colors.BLUE_700)
                )

        #Técnicos
        if not tecnicos:
            listado_tecn.controls.append(ft.Text("Sin técnicos", color="grey"))
        else:
            for u in tecnicos:
                listado_tecn.controls.append(
                    ft.Text(f"ID: {u['id']} - {u['login']}", color=ft.Colors.TEAL_700, weight=ft.FontWeight.W_500)
                )

        #Admins
        if not administradores:
            listado_admin.controls.append(ft.Text("Sin admins", color="grey"))
        else:
            for u in administradores:
                listado_admin.controls.append(
                    ft.Text(f"ID: {u['id']} - {u['login']}", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)
                )

        page.update()

    #--- MANEJADORES ---
    def manejar_añadir(e):
        msg_add.value = ""
        ok_mig, _ = controller.comprobar_migracion()
        if not ok_mig:
            msg_add.value = "⚠️ Bloqueado: requiere migración."
            page.update()
            return

        payload = {
            "nombre": campo_nombre.value.strip(),
            "apellidos": campo_apellidos.value.strip(),
            "login": campo_login.value.strip(),
            "rol": dropdown_rol.value,
            "hash": hashlib.sha256(campo_pass.value.encode()).hexdigest(),
        }

        if not confirm_add["active"] or confirm_add["data"] != payload:
            confirm_add["active"], confirm_add["data"] = True, payload
            msg_add.value = f"¿Confirmar {payload['rol']} '{payload['login']}'?"
            msg_add.color = ft.Colors.ORANGE_800
            page.update()
            return

        ok, res = controller.crear_usuario(payload)
        if ok:
            msg_add.value = f"✅ Creado con ID: {res}"
            msg_add.color = ft.Colors.GREEN_700
            for c in [campo_nombre, campo_apellidos, campo_login, campo_pass]: c.value = ""
            refrescar()
        else:
            msg_add.value = f"❌ {res}"
            msg_add.color = ft.Colors.RED_700
        
        confirm_add["active"] = False
        page.update()

    def manejar_eliminar(e):
        msg_del.value = ""
        user_id_str = campo_id_del.value.strip()

        if not user_id_str:
            msg_del.value = "⚠️ Indica un ID de usuario."
            msg_del.color = ft.Colors.RED_700
            page.update()
            return

        try:
            user_id = int(user_id_str)
        except ValueError:
            msg_del.value = "⚠️ El ID debe ser un número."
            msg_del.color = ft.Colors.RED_700
            page.update()
            return

        #Lógica de confirmación (Doble clic)
        if not confirm_del["active"] or confirm_del["id"] != user_id:
            confirm_del["active"], confirm_del["id"] = True, user_id
            msg_del.value = f"¿Seguro que quieres eliminar al ID {user_id}? Pulsa otra vez."
            msg_del.color = ft.Colors.ORANGE_800
            page.update()
            return

        #Llamada al controller
        ok, res = controller.eliminar_usuario(user_id)
        if ok:
            msg_del.value = f"✅ Usuario {user_id} eliminado."
            msg_del.color = ft.Colors.GREEN_700
            campo_id_del.value = ""
            refrescar()
        else:
            msg_del.value = f"❌ {res}"
            msg_del.color = ft.Colors.RED_700
        
        confirm_del["active"] = False
        page.update()

    #--- ESTRUCTURA ---
    btn_add = ft.ElevatedButton("Registrar Usuario", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color="white", width=W_LEFT, on_click=manejar_añadir)
    btn_eliminar = ft.ElevatedButton("Eliminar Permanentemente", icon=ft.Icons.DELETE_FOREVER, bgcolor=ft.Colors.RED_700, color="white", width=W_LEFT, on_click=manejar_eliminar)

    panel_gestion = ft.Container(
        width=W_LEFT + 20,
        content=ft.Column([
            ft.Text("Alta de Usuarios", size=18, weight="bold", color=ft.Colors.BLUE_700),
            ft.Row([campo_nombre, campo_apellidos]),
            ft.Row([campo_login, campo_pass]),
            dropdown_rol,
            btn_add,
            msg_add,
            ft.Divider(height=20),
            ft.Text("Eliminar Usuario", size=18, weight="bold", color=ft.Colors.RED_700),
            ft.Row([campo_id_del]),
            btn_eliminar,
            msg_del
        ], spacing=10)
    )

    panel_listados = ft.Row(
        [
            crear_contenedor_lista("Trabajadores", ft.Colors.BLUE_700, ft.Icons.PERSON, listado_trab),
            crear_contenedor_lista("Técnicos", ft.Colors.TEAL_700, ft.Icons.ENGINEERING, listado_tecn),
            crear_contenedor_lista("Administradores", ft.Colors.RED_700, ft.Icons.SECURITY, listado_admin),
        ],
        expand=True,
        spacing=15
    )

    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit="cover", expand=True),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                padding=20,
                content=ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=20,
                    padding=25,
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: on_volver()),
                            ft.Text("Gestión de Usuarios y Roles", size=24, weight="bold"),
                        ], alignment="spaceBetween"),
                        ft.Divider(),
                        ft.Row([panel_gestion, panel_listados], expand=True, vertical_alignment="start")
                    ])
                )
            )
        ], expand=True)
    )

    refrescar()