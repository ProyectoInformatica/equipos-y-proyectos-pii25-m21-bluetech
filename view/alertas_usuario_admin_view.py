import flet as ft
from controller.ticket_controller import TicketController
import asyncio

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()
    page.bgcolor = "#F0F2F5"

    auto_refresh_running = {"value": True}

    rol_map = {
        "trabajador": 1,
        "administrador": 2,
        "tecnico": 3
    }
    rol_usuario = rol_map.get(usuario.rol)

    controller = TicketController()
    ticket_actual = {"id": None}

    mensajes_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    tickets_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    escribiendo = {"valor": False}

    def escribir(valor):
        escribiendo["valor"] = valor

    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True,
        border_radius=25,
        bgcolor=ft.Colors.GREY_50,
        on_focus=lambda e: escribir(True),
        on_blur=lambda e: escribir(False),
        on_submit=lambda e: page.run_task(enviar_mensaje, e)
    )

    campo_ticket = ft.TextField(
        hint_text="¿En qué podemos ayudarte?",
        expand=True,
        border_radius=10,
        bgcolor=ft.Colors.GREY_50,
        on_submit=lambda e: page.run_task(crear_ticket, e)
    )

    boton_asignar = ft.ElevatedButton(
        "Asignarme ticket",
        icon=ft.Icons.ASSIGNMENT_IND,
        visible=False,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
    )

    boton_cerrar = ft.ElevatedButton(
        "Cerrar ticket",
        icon=ft.Icons.CLOSE,
        visible=False,
        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
    )

    boton_redirigir = ft.ElevatedButton(
        "Redirigir",
        icon=ft.Icons.SWAP_HORIZ,
        visible=False
    )

    def volver_menu(e):
        auto_refresh_running["value"] = False
        mostrar_pantalla_menu_admin(page, repo, usuario)

    async def cargar_mensajes(id_ticket, limpiar=False):
        if limpiar:
            mensajes_column.controls.clear()
            # Al limpiar, pedimos la carga completa del historial
            lista_msj = controller.actualizar_chat(id_ticket, solo_nuevos=False)
        else:
            # En el auto-refresh, pedimos solo lo nuevo
            lista_msj = controller.actualizar_chat(id_ticket, solo_nuevos=True)
        if not lista_msj:
            return
        # Ahora simplemente recorremos lo que recibimos
        for m in lista_msj:
            es_mio = m["id_emisor"] == usuario.id_usuario
            burbuja = ft.Row(
                alignment=ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Text(m["nombre_emisor"], size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                            ft.Text(m["texto"], size=14, selectable=True),
                            ft.Text(m["fecha_hora"], size=9, color=ft.Colors.GREY_600),
                        ], spacing=3, tight=True),
                        bgcolor="#DCF8C6" if es_mio else ft.Colors.WHITE,
                        padding=12,
                        width=320,
                        border_radius=ft.border_radius.only(
                            top_left=15, top_right=15,
                            bottom_left=15 if es_mio else 2,
                            bottom_right=2 if es_mio else 15
                        ),
                        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.with_opacity(0.1, "black"))
                    )
                ]
            )
            mensajes_column.controls.append(burbuja)
        page.update()
        # Hacemos scroll si añadimos mensajes
        await mensajes_column.scroll_to(offset=-1, duration=500)

    async def seleccionar_ticket(ticket):
        ticket_actual["id"] = ticket["id_ticket"]
        ticket_actual["data"] = ticket
        soy_el_creador = int(ticket.get("id_emisor") or 0) == int(usuario.id_usuario)
        es_pendiente = ticket["estado"] == "pendiente"
        es_cerrado = ticket["estado"] == "cerrado"
        soy_el_asignado = int(ticket.get("id_destinatario") or 0) == int(usuario.id_usuario)
        boton_asignar.visible = es_pendiente and not soy_el_creador
        boton_cerrar.visible = not es_cerrado and not soy_el_creador
        boton_redirigir.visible = not es_cerrado and soy_el_asignado
        await cargar_mensajes(ticket["id_ticket"], limpiar=True)
        actualizar_input_bar()
        page.update()

    async def asignarme_ticket(e):
        if ticket_actual["id"]:
            controller.asignar_ticket(ticket_actual["id"], usuario)
            cargar_tickets()
            todos = controller.obtener_todos_los_tickets()
            ticket_actual["data"] = next(
                (t for t in todos if t["id_ticket"] == ticket_actual["id"]),
                ticket_actual["data"]
            )
            await seleccionar_ticket(ticket_actual["data"])

    boton_asignar.on_click = asignarme_ticket

    def cargar_tickets():
        controller.obtener_tickets_procesados(usuario, rol_usuario)
        todos = controller.obtener_todos_los_tickets()
        tickets_column.controls.clear()
        activos = []
        cerrados = []
        for ticket in todos:
            es_creador = int(ticket.get("id_emisor") or 0) == int(usuario.id_usuario)
            es_asignado = int(ticket.get("id_destinatario") or 0) == int(usuario.id_usuario)
            esta_libre = not ticket.get("id_destinatario")
            # 🔵 ACTIVOS
            if ticket["estado"] != "cerrado":
                if esta_libre or es_asignado or es_creador:
                    activos.append(ticket)
            # 🔴 CERRADOS (solo los creados por el usuario)
            elif es_creador:
                cerrados.append(ticket)
        # --- ACTIVOS ---
        tickets_column.controls.append(
            ft.Text("🟢 Activos:", size=18, weight=ft.FontWeight.BOLD)
        )
        for ticket in activos:
            tickets_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.REPORT_PROBLEM_OUTLINED),
                    title=ft.Text(ticket["descripcion"], max_lines=1),
                    subtitle=ft.Text(f"Estado: {ticket['estado']}"),
                    on_click=lambda e, t=ticket: page.run_task(seleccionar_ticket, t),
                )
            )
        # --- CERRADOS ---
        tickets_column.controls.append(ft.Divider(height=20))
        tickets_column.controls.append(
            ft.Text("🔴 Cerrados", size=18, weight=ft.FontWeight.BOLD)
        )
        for ticket in cerrados:
            tickets_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="grey"),
                    title=ft.Text(ticket["descripcion"], max_lines=1),
                    subtitle=ft.Text(f"Estado: {ticket['estado']}"),
                    on_click=lambda e, t=ticket: page.run_task(seleccionar_ticket, t),
                )
            )
        page.update()

    async def crear_ticket(e):
        descripcion = campo_ticket.value.strip()
        if not descripcion:
            return
        controller.crear_ticket(usuario, descripcion, 3)
        campo_ticket.value = ""
        cargar_tickets()
        page.snack_bar = ft.SnackBar(ft.Text("Ticket creado correctamente"))
        page.snack_bar.open = True
        page.update()

    input_row = ft.Container()

    def actualizar_input_bar():
        if not ticket_actual.get("data"):
            input_row.content = ft.Text("Selecciona un ticket")
            page.update()
            return
        t = ticket_actual["data"]
        es_creador = int(t.get("id_emisor") or 0) == int(usuario.id_usuario)
        es_asignado = int(t.get("id_destinatario") or 0) == int(usuario.id_usuario)
        puedo_escribir = es_creador or es_asignado
        if t["estado"] == "cerrado":
            input_row.content = ft.Text("Ticket cerrado", color="red")
        elif not puedo_escribir:
            input_row.content = ft.Container(
                content=ft.Text("No puedes escribir: No estás asignado a este ticket", color="orange"),
                padding=10, bgcolor=ft.Colors.AMBER_50, border_radius=10
            )
        else:
            input_row.content = ft.Row([input_mensaje, ft.FloatingActionButton(icon=ft.Icons.SEND, on_click=enviar_mensaje)])
        page.update()

    async def redirigir_ticket(e):
        if not ticket_actual["id"]:
            return
        # 🔥 1. Acción backend
        controller.redirigir_ticket(ticket_actual["id"], 3)
        # 🔥 2. LIMPIAR ESTADO DEL CHAT (CLAVE)
        ticket_actual["id"] = None
        ticket_actual["data"] = None
        mensajes_column.controls.clear()
        boton_asignar.visible = False
        boton_cerrar.visible = False
        boton_redirigir.visible = False
        # 🔥 3. RESET INPUT
        input_row.content = ft.Text("Selecciona un ticket")
        # 🔥 4. REFRESH LISTA
        cargar_tickets()
        # 🔥 5. UI FEEDBACK
        page.snack_bar = ft.SnackBar(ft.Text("Ticket redirigido a técnicos"))
        page.snack_bar.open = True
        page.update()

    boton_redirigir.on_click = redirigir_ticket

    async def cerrar_ticket(e):
        if not ticket_actual["id"]:
            return
        controller.cerrar_ticket(ticket_actual["id"])
        cargar_tickets()
        todos = controller.obtener_todos_los_tickets()
        ticket_actual["data"] = next(
            (t for t in todos if t["id_ticket"] == ticket_actual["id"]),
            ticket_actual["data"]
        )
        await seleccionar_ticket(ticket_actual["data"])
        page.snack_bar = ft.SnackBar(ft.Text("Ticket cerrado"))
        page.snack_bar.open = True
        page.update()

    boton_cerrar.on_click = cerrar_ticket

    async def enviar_mensaje(e):
        if not ticket_actual["id"] or not input_mensaje.value.strip():
            return
        if ticket_actual["data"]["estado"] == "cerrado":
            page.snack_bar = ft.SnackBar(ft.Text("Este ticket está cerrado"))
            page.snack_bar.open = True
            page.update()
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        await cargar_mensajes(ticket_actual["id"])

    async def auto_refresh():
        while auto_refresh_running["value"]:
            await asyncio.sleep(2)
            controller.tickets_cache.clear()
            cargar_tickets()
            if ticket_actual.get("id"):
                await cargar_mensajes(ticket_actual["id"], limpiar=False)
            page.update()

    panel_tickets = ft.Container(
        expand=1,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=15,
        content=ft.Column([
            ft.Text("Mis Reportes", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                campo_ticket,
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=lambda e: page.run_task(crear_ticket, e),
                    mini=True,
                    bgcolor=ft.Colors.GREEN_700,
                    tooltip="Crear Ticket"
                )
            ], spacing=10),
            ft.Divider(height=20),
            tickets_column
        ])
    )

    panel_mensajeria = ft.Container(
        expand=3,
        bgcolor="#E5DDD5",
        border_radius=15,
        padding=15,
        content=ft.Column([
            ft.Text("Chat con Soporte", size=20, weight=ft.FontWeight.BOLD),
            mensajes_column,
            input_row,
            ft.Row([
                boton_asignar,
                boton_cerrar,
                boton_redirigir
            ], alignment=ft.MainAxisAlignment.CENTER),
        ])
    )

    page.add(
        ft.Container(
            expand=True,
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text("Centro de Ayuda BlueTech", size=28, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_menu)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([panel_tickets, panel_mensajeria], expand=True)
            ])
        )
    )

    cargar_tickets()

    if not getattr(page, "auto_started", False):
        page.auto_started = True
        page.run_task(auto_refresh)