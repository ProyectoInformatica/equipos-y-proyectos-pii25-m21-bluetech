import flet as ft
from controller.ticket_controller import TicketController

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    page.clean()
    page.bgcolor = "#F0F2F5"
    controller = TicketController()
    ticket_actual = {"id": None, "data": None}
    
    #--- Componentes de la interfaz ---
    mensajes_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    tickets_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True,
        border_radius=25,
        on_submit=lambda e: page.run_task(enviar_mensaje, e),
        bgcolor=ft.Colors.GREY_50
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

    def volver_menu(e):
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    def cerrar_ticket(e):
        if ticket_actual["id"]:
            controller.cerrar_ticket(ticket_actual["id"])
            cargar_tickets()
            mensajes_column.controls.clear()
            ticket_actual["id"] = None
            boton_cerrar.visible = False
            boton_asignar.visible = False
            page.update()

    input_row = ft.Container()
    def actualizar_input_bar():
        if not ticket_actual["data"]:
            input_row.content = ft.Text("Selecciona un ticket")
        elif ticket_actual["data"].get("id_tecnico") != usuario.id_usuario:
            input_row.content = ft.Container(
                content=ft.Text(
                    "⚠️ Debes asignarte este ticket para responder",
                    color=ft.Colors.ORANGE_700
                ),
                padding=10
            )
        else:
            input_row.content = ft.Row([
                input_mensaje,
                ft.FloatingActionButton(
                    on_click=lambda e: page.run_task(enviar_mensaje, e),
                    bgcolor=ft.Colors.BLUE_700,
                    content=ft.Icon(ft.Icons.SEND_ROUNDED, color="white", size=20)
                )
            ], spacing=10)
        page.update()

    def crear_ticket(e):
        descripcion = campo_ticket.value.strip()
        if not descripcion:
            return

        controller.crear_ticket(usuario, descripcion)
        campo_ticket.value = ""
        cargar_tickets()

        page.snack_bar = ft.SnackBar(ft.Text("Ticket creado correctamente"))
        page.snack_bar.open = True
        page.update()

    boton_cerrar.on_click = cerrar_ticket

    #--- Lógica de Mensajes ---
    async def cargar_mensajes(id_ticket):
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_ticket)
        for m in mensajes:
            es_tecnico = m["rol"] == "tecnico"
            burbuja = ft.Row(
                alignment=ft.MainAxisAlignment.END if es_tecnico else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Text(m["nombre_emisor"], size=11, weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.BLUE_GREY_700),
                            ft.Text(m["texto"], size=14, selectable=True),
                            ft.Text(m["fecha_hora"], size=9, color=ft.Colors.GREY_600, text_align=ft.TextAlign.RIGHT),
                        ], spacing=3, tight=True),
                        bgcolor="#DCF8C6" if es_tecnico else ft.Colors.WHITE,
                        padding=12,
                        width=320,
                        border_radius=ft.border_radius.only(
                            top_left=15, top_right=15,
                            bottom_left=15 if es_tecnico else 2,
                            bottom_right=2 if es_tecnico else 15
                        ),
                        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.with_opacity(0.1, "black"))
                    )
                ]
            )
            mensajes_column.controls.append(burbuja)
        page.update()
        await mensajes_column.scroll_to(offset=-1, duration=500)

    async def seleccionar_ticket(ticket):
        ticket_actual["id"] = ticket["id_ticket"]
        ticket_actual["data"] = ticket
        boton_asignar.visible = (ticket["estado"] == "pendiente")
        boton_cerrar.visible = (ticket["estado"] != "cerrado")
        await cargar_mensajes(ticket["id_ticket"])
        actualizar_input_bar()
        page.update()

    def cargar_tickets():
        tickets_column.controls.clear()
        tickets = controller.obtener_tickets()
        for ticket in tickets:
            if ticket["estado"] != "cerrado" and (ticket["estado"] == "pendiente" or ticket.get("id_tecnico") == usuario.id_usuario):
                tickets_column.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CONFIRMATION_NUMBER_OUTLINED),
                        title=ft.Text(ticket["descripcion"], weight=ft.FontWeight.W_500),
                        subtitle=ft.Text(f"{ticket['nombre_emisor']} • {ticket['estado']}"),
                        on_click=lambda e, a=ticket: page.run_task(seleccionar_ticket, a),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                )
        page.update()

    async def enviar_mensaje(e):
        if not ticket_actual["id"] or not input_mensaje.value.strip():
            return
        # 🔴 NUEVO CONTROL
        if ticket_actual["data"].get("id_tecnico") != usuario.id_usuario:
            page.snack_bar = ft.SnackBar(
                ft.Text("Debes asignarte el ticket antes de responder")
            )
            page.snack_bar.open = True
            page.update()
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        await input_mensaje.focus()
        await cargar_mensajes(ticket_actual["id"])

    def asignarme_ticket(e):
        if ticket_actual["id"]:
            controller.asignar_ticket(ticket_actual["id"], usuario)
            cargar_tickets()
            boton_asignar.visible = False
            page.update()

    boton_asignar.on_click = asignarme_ticket

    #--- Construcción del Layout ---
    panel_tickets = ft.Container(
        expand=1,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=15,
        content=ft.Column([
            ft.Text("Tickets", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                campo_ticket,
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=crear_ticket,
                    mini=True,
                    bgcolor=ft.Colors.GREEN_700,
                    tooltip="Crear Ticket"
                )
            ], spacing=10),
            ft.Divider(height=1),
            tickets_column
        ])
    )

    panel_mensajeria = ft.Container(
        expand=3,
        bgcolor="#E5DDD5",
        border_radius=15,
        padding=15,
        content=ft.Column([
            ft.Text("Chat de Soporte", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=1, color="#E5DDD5"),
            mensajes_column,
            ft.Row([
                input_row
            ], spacing=10),
            ft.Row([
                boton_asignar,
                boton_cerrar
            ], alignment=ft.MainAxisAlignment.CENTER),
        ])
    )

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
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=volver_menu)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([panel_tickets, panel_mensajeria], expand=True, spacing=15)
            ], expand=True)
        )
    )

    cargar_tickets()