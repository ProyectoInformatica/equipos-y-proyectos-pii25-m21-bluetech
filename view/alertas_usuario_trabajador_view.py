import flet as ft
from controller.ticket_controller import TicketController

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    page.clean()
    page.bgcolor = "#F0F2F5"

    controller = TicketController()
    ticket_actual = {"id": None}
    
    #--- Componentes de la interfaz ---
    mensajes_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    tickets_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True,
        border_radius=25,
        bgcolor=ft.Colors.GREY_50,
        on_submit=lambda e: page.run_task(enviar_mensaje, e)
    )
    
    campo_ticket = ft.TextField(
        hint_text="¿En qué podemos ayudarte?",
        expand=True,
        border_radius=10,
        bgcolor=ft.Colors.GREY_50,
        on_submit=lambda e: crear_ticket(e)
    )

    #VOLVER
    def volver_menu(e):
        mostrar_pantalla_menu_trabajador(page, repo, usuario)

    #CARGAR MENSAJES
    async def cargar_mensajes(id_ticket):
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
        await mensajes_column.scroll_to(offset=-1, duration=500)

    async def seleccionar_ticket(ticket):
        ticket_actual["id"] = ticket["id_ticket"]
        ticket_actual["estado"] = ticket["estado"]
        await cargar_mensajes(ticket["id_ticket"])
        actualizar_input_bar()
        page.update()

    def cargar_tickets():
        tickets_column.controls.clear()
        tickets = controller.obtener_tickets_usuario(usuario.id_usuario)
        activos = []
        cerrados = []
        for ticket in tickets:
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

    def crear_ticket(e):
        descripcion = campo_ticket.value.strip()
        if not descripcion: return
        controller.crear_ticket(usuario, descripcion)
        campo_ticket.value = ""
        cargar_tickets()
        page.snack_bar = ft.SnackBar(ft.Text("Ticket creado correctamente"))
        page.snack_bar.open = True
        page.update()

    input_row = ft.Container()
    def actualizar_input_bar():
        if ticket_actual.get("estado") == "cerrado":
            input_row.content = ft.Container(
                content=ft.Text(
                    "🔴 Este ticket está cerrado (solo lectura)",
                    color=ft.Colors.RED_700
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
        if not ticket_actual["id"]:
            return
        #si está cerrado no permite enviar
        if ticket_actual.get("estado") == "cerrado":
            page.snack_bar = ft.SnackBar(
                ft.Text("Este ticket está cerrado. No puedes enviar mensajes.")
            )
            page.snack_bar.open = True
            page.update()
            return
        if not input_mensaje.value.strip():
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        await input_mensaje.focus()
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
            ], spacing=10)
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

    cargar_tickets()