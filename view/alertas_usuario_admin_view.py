import flet as ft
from controller.ticket_controller import TicketController
import asyncio

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()
    page.bgcolor = "#F0F2F5"

    controller = TicketController()
    ticket_actual = {"id": None}
    
    #--- Componentes de la interfaz ---
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
        on_submit=lambda e: crear_ticket(e)
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

    #VOLVER
    def volver_menu(e):
        mostrar_pantalla_menu_admin(page, repo, usuario)

    #CARGAR MENSAJES
    async def cargar_mensajes(id_ticket):
        try:
            _ = mensajes_column.page
        except:
            return
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_ticket)
        for m in mensajes:
            es_mio = m["id_emisor"] == usuario.id_usuario
            burbuja = ft.Row(
                alignment=ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Text(m["nombre_emisor"], size=11, weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.BLUE_GREY_700),
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
        try:
            await mensajes_column.scroll_to(offset=-1, duration=500)
        except:
            pass

    async def seleccionar_ticket(ticket):
        ticket_actual["id"] = ticket["id_ticket"]
        ticket_actual["data"] = ticket
        # --- LÓGICA DE VISIBILIDAD ---
        soy_el_creador = int(ticket.get("id_emisor")) == int(usuario.id_usuario)
        es_pendiente = ticket["estado"] == "pendiente"
        es_cerrado = ticket["estado"] == "cerrado"
        soy_el_asignado = ticket.get("id_destinatario") == usuario.id_usuario
        boton_asignar.visible = es_pendiente and not soy_el_creador
        boton_cerrar.visible = not es_cerrado and not soy_el_creador
        boton_redirigir.visible = not es_cerrado and soy_el_asignado
        await cargar_mensajes(ticket["id_ticket"])
        actualizar_input_bar()
        page.update()

    def deseleccionar_ticket():
        ticket_actual["id"] = None
        ticket_actual["data"] = None
        mensajes_column.controls.clear()
        boton_asignar.visible = False
        boton_cerrar.visible = False
        boton_redirigir.visible = False
        actualizar_input_bar()
        page.update()

    async def asignarme_ticket(e):
        if ticket_actual["id"]:
            controller.asignar_ticket(ticket_actual["id"], usuario)
            cargar_tickets(usuario.id_usuario)
            tickets = controller.obtener_tickets_admin(usuario.id_usuario)
            ticket_actual["data"] = next(
                (t for t in tickets if t["id_ticket"] == ticket_actual["id"]),
                ticket_actual["data"]
            )
            await seleccionar_ticket(ticket_actual["data"])
            boton_asignar.visible = False
            page.update()
    
    boton_asignar.on_click = asignarme_ticket

    def cargar_tickets(id_usuario):
        tickets_column.controls.clear()
        tickets = controller.obtener_tickets_admin(id_usuario)
        activos = []
        cerrados = []
        for ticket in tickets:
            id_asignado = ticket.get("id_destinatario")
            id_creador = ticket.get("id_emisor")
            usuario_id_int = int(usuario.id_usuario)
            # --- FILTRO DE PRIVACIDAD ---
            if (id_asignado is None or int(id_asignado) == usuario_id_int or int(id_creador) == usuario_id_int):
                if ticket["estado"] == "cerrado":
                    cerrados.append(ticket)
                else:
                    activos.append(ticket)
        # --- ACTIVOS ---
        tickets_column.controls.append(
            ft.Text("🟢 Activos:", size=18, weight=ft.FontWeight.BOLD)
        )
        for ticket in activos:
            tickets_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.REPORT_PROBLEM_OUTLINED, 
                                    color="orange" if ticket["estado"] == "pendiente" else "blue"),
                    title=ft.Text(ticket["descripcion"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    subtitle=ft.Text(f"Estado: {ticket['estado']}"),
                    on_click=lambda e, t=ticket: page.run_task(seleccionar_ticket, t),
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        # --- CERRADOS ---
        tickets_column.controls.append(
            ft.Divider(height=20)
        )
        tickets_column.controls.append(
            ft.Text("🔴 Cerrados", size=18, weight=ft.FontWeight.BOLD)
        )
        for ticket in cerrados:
            tickets_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.REPORT_PROBLEM_OUTLINED, 
                                    color="orange" if ticket["estado"] == "pendiente" else "blue"),
                    title=ft.Text(ticket["descripcion"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    subtitle=ft.Text(f"Estado: {ticket['estado']}"),
                    on_click=lambda e, t=ticket: page.run_task(seleccionar_ticket, t),
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        page.update()

    def redirigir(e):
        if ticket_actual["id"]:
            nuevo_rol = 2 if usuario.rol == "tecnico" else 3
            controller.redirigir_ticket(ticket_actual["id"], nuevo_rol)
            cargar_tickets(usuario.id_usuario)
            deseleccionar_ticket() 

    def cerrar_ticket(e):
        if ticket_actual["id"]:
            controller.cerrar_ticket(ticket_actual["id"])
            cargar_tickets(usuario.id_usuario)
            deseleccionar_ticket() 
            mensajes_column.controls.clear()
            ticket_actual["id"] = None
            boton_cerrar.visible = False
            boton_asignar.visible = False
            page.update()

    boton_cerrar.on_click = cerrar_ticket
    boton_redirigir.on_click = redirigir

    def crear_ticket(e):
        descripcion = campo_ticket.value.strip()
        if not descripcion: 
            return
        rol_destino = 3
        controller.crear_ticket(usuario, descripcion, rol_destino)
        campo_ticket.value = ""
        cargar_tickets(usuario.id_usuario)
        page.snack_bar = ft.SnackBar(ft.Text("Ticket creado correctamente"))
        page.snack_bar.open = True
        page.update()

    input_row = ft.Container()
    def actualizar_input_bar():
        if not ticket_actual.get("data"):
            input_row.content = ft.Text("Selecciona un ticket")
            page.update()
            return
        id_asignado = ticket_actual["data"].get("id_destinatario")
        if id_asignado is not None:
            id_asignado = int(id_asignado)
        data = ticket_actual["data"]
        estado = data.get("estado")
        usuario_id = int(usuario.id_usuario)
        id_creador = int(data.get("id_emisor")) if data.get("id_emisor") else None
        id_asignado = int(data.get("id_destinatario")) if data.get("id_destinatario") else None
        if estado == "cerrado":
            input_row.content = ft.Container(
                content=ft.Text(
                    "🔴 Este ticket está cerrado (solo lectura)",
                    color=ft.Colors.RED_700
                ),
                padding=10
            )
        elif usuario_id != id_creador and usuario_id != id_asignado:
            input_row.content = ft.Container(
                content=ft.Text(
                    "⚠️ Debes estar asignado al ticket para responder",
                    color=ft.Colors.ORANGE_700
                ),
                padding=10
            )
        else:
            input_row.content = ft.Row([
                input_mensaje,
                ft.FloatingActionButton(
                    on_click=enviar_mensaje,
                    bgcolor=ft.Colors.BLUE_700,
                    content=ft.Icon(ft.Icons.SEND_ROUNDED, color="white", size=20)
                )
            ], spacing=10)
        page.update()

    async def enviar_mensaje(e):
        if not ticket_actual["id"] or not input_mensaje.value.strip():
            return
        #si está cerrado no permite enviar
        data = ticket_actual["data"]
        usuario_id = str(usuario.id_usuario)
        id_creador = str(data.get("id_emisor"))
        id_asignado = str(data.get("id_destinatario"))
        if data.get("estado") == "cerrado":
            page.snack_bar = ft.SnackBar(ft.Text("Este ticket está cerrado"))
            page.snack_bar.open = True
            page.update()
            return
        if usuario_id != id_creador and usuario_id != id_asignado:
            page.snack_bar = ft.SnackBar(
                ft.Text("No tienes permiso para comentar en este ticket")
            )
            page.snack_bar.open = True
            page.update()
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        await input_mensaje.focus()
        await cargar_mensajes(ticket_actual["id"])

    async def auto_refresh():
        while True:
            await asyncio.sleep(3)
            try:
                _ = page.controls
            except:
                break
            cargar_tickets(usuario.id_usuario if hasattr(usuario, "id_usuario") else None)
            if ticket_actual.get("id"):
                tickets = controller.obtener_tickets_usuario(usuario.id_usuario)
                ticket = next((t for t in tickets if t["id_ticket"] == ticket_actual["id"]), None)

                if ticket:
                    ticket_actual["estado"] = ticket["estado"]
                    if ticket["estado"] == "cerrado":
                        actualizar_input_bar()

                if not escribiendo["valor"]:
                    await cargar_mensajes(ticket_actual["id"])

    #--- Diseño de Paneles ---
    panel_tickets = ft.Container(
        expand=1,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=15,
        content=ft.Column([
            ft.Text("Mis Reportes", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                campo_ticket,
                ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=crear_ticket, mini=True, 
                                        bgcolor=ft.Colors.GREEN_700, tooltip="Crear Ticket")
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
            ft.Divider(height=1, color=ft.Colors.GREY_400),
            mensajes_column,
            ft.Row([
                input_row,
            ], spacing=10),
            ft.Row([
                boton_asignar,
                boton_cerrar,
                boton_redirigir
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], expand=True)
    )

    #--- Header y Main Layout ---
    page.add(
        ft.Container(
            expand=True,
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.SUPPORT_AGENT, size=30, color=ft.Colors.BLUE_700),
                        ft.Text("Centro de Ayuda BlueTech", size=28, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_menu, tooltip="Volver al Menú")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([panel_tickets, panel_mensajeria], expand=True, spacing=15)
            ], expand=True)
        )
    )

    cargar_tickets(usuario.id_usuario)
    page.run_task(auto_refresh)