import flet as ft
from controller.alertas_usuario_controller import AlertasUsuarioController

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    page.clean()
    page.bgcolor = "#F0F2F5"

    controller = AlertasUsuarioController()
    ticket_actual = {"id": None}
    
    #--- Componentes de la interfaz ---
    mensajes_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    tickets_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True,
        border_radius=25,
        bgcolor=ft.Colors.GREY_50,
        on_submit=lambda e: enviar_mensaje(e)
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
    def cargar_mensajes(id_alerta):
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_alerta)
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
        mensajes_column.scroll_to(offset=-1, duration=500)

    def seleccionar_ticket(alerta):
        ticket_actual["id"] = alerta["id_alerta"]
        cargar_mensajes(alerta["id_alerta"])

    def cargar_tickets():
        tickets_column.controls.clear()
        alertas = controller.obtener_alertas_usuario(usuario.id_usuario)
        for alerta in alertas:
            tickets_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.REPORT_PROBLEM_OUTLINED, 
                                    color="orange" if alerta["estado"] == "pendiente" else "blue"),
                    title=ft.Text(alerta["descripcion"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    subtitle=ft.Text(f"Estado: {alerta['estado']}"),
                    on_click=lambda e, a=alerta: seleccionar_ticket(a),
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        page.update()

    def crear_ticket(e):
        descripcion = campo_ticket.value.strip()
        if not descripcion: return
        controller.crear_alerta(usuario, descripcion)
        campo_ticket.value = ""
        cargar_tickets()
        page.snack_bar = ft.SnackBar(ft.Text("Ticket creado correctamente"))
        page.snack_bar.open = True
        page.update()

    def enviar_mensaje(e):
        if not ticket_actual["id"] or not input_mensaje.value.strip():
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        input_mensaje.focus()
        cargar_mensajes(ticket_actual["id"])

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
                input_mensaje,
                ft.FloatingActionButton(
                    icon=ft.Icons.SEND_ROUNDED, 
                    on_click=enviar_mensaje,
                    bgcolor=ft.Colors.BLUE_700,
                    content=ft.Icon(ft.Icons.SEND_ROUNDED, color="white", size=20)
                )
            ], spacing=10)
        ], expand=True)
    )

    #--- Header y Main Layout ---
    page.add(
        ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SUPPORT_AGENT, size=30, color=ft.Colors.BLUE_700),
                    ft.Text("Centro de Ayuda BlueTech", size=28, weight=ft.FontWeight.BOLD),
                ]),
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=volver_menu, tooltip="Volver al Menú")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([panel_tickets, panel_mensajeria], expand=True, spacing=15)
        ], expand=True, padding=10)
    )

    cargar_tickets()