import flet as ft
from controller.alertas_usuario_controller import AlertasUsuarioController

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    page.clean()
    page.bgcolor = "#f5f7fa"

    controller = AlertasUsuarioController()
    ticket_actual = {"id": None}
    mensajes_column = ft.Column(scroll="auto", expand=True)
    tickets_column = ft.Column(scroll="auto", expand=True)
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True
    )
    campo_ticket = ft.TextField(
        hint_text="Describe tu problema...",
        expand=True
    )

    # VOLVER
    def volver_menu(e):
        mostrar_pantalla_menu_trabajador(page, repo, usuario)

    # CARGAR MENSAJES
    def cargar_mensajes(id_alerta):
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_alerta)
        for m in mensajes:
            es_usuario = m["id_emisor"] == usuario.id_usuario
            mensaje = ft.Row(
                alignment=ft.MainAxisAlignment.END if es_usuario else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=350,  
                        bgcolor="#d2f8d2" if es_usuario else "#e9f5ff",
                        padding=10,
                        border_radius=ft.border_radius.only(
                            top_left=10,
                            top_right=10,
                            bottom_left=10 if es_usuario else 0,
                            bottom_right=0 if es_usuario else 10
                        ),
                        content=ft.Column(
                            [
                                ft.Text(m["nombre_emisor"], size=12, weight="bold"),
                                ft.Text(
                                    m["texto"],
                                    selectable=True,
                                    expand=False
                                ),
                                ft.Text(m["fecha_hora"], size=10, color="grey")
                            ],
                            tight=True
                        )
                    )
                ]
            )
            mensajes_column.controls.append(mensaje)
        page.update()

    # SELECCIONAR TICKET
    def seleccionar_ticket(alerta):
        ticket_actual["id"] = alerta["id_alerta"]
        cargar_mensajes(alerta["id_alerta"])

    # CARGAR TICKETS
    def cargar_tickets():
        tickets_column.controls.clear()
        alertas = controller.obtener_alertas_usuario(usuario.id_usuario)
        for alerta in alertas:
            ticket = ft.ListTile(
                title=ft.Text(alerta["descripcion"]),
                subtitle=ft.Text(f"Estado: {alerta['estado']}"),
                on_click=lambda e, a=alerta: seleccionar_ticket(a)
            )
            tickets_column.controls.append(ticket)
        page.update()

    # CREAR TICKET
    def crear_ticket(e):
        descripcion = campo_ticket.value.strip()
        if descripcion == "":
            return
        controller.crear_alerta(usuario, descripcion)
        campo_ticket.value = ""
        cargar_tickets()

    # ENVIAR MENSAJE
    def enviar_mensaje(e):
        if ticket_actual["id"] is None:
            return
        texto = input_mensaje.value.strip()
        if texto == "":
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], texto)
        input_mensaje.value = ""
        cargar_mensajes(ticket_actual["id"])

    panel_tickets = ft.Container(
        expand=1,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            [
                ft.Text("Mis Tickets", size=22, weight="bold"),
                ft.Divider(),
                ft.Row(
                    [
                        campo_ticket,
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            on_click=crear_ticket
                        )
                    ]
                ),
                ft.Divider(),
                tickets_column
            ]
        )
    )

    panel_mensajeria = ft.Container(
        expand=3,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            [
                ft.Text("Conversación", size=22, weight="bold"),
                ft.Divider(),
                mensajes_column,
                ft.Row(
                    [
                        input_mensaje,
                        ft.IconButton(
                            icon=ft.Icons.SEND,
                            on_click=enviar_mensaje
                        )
                    ]
                )
            ],
            expand=True
        )
    )

    header = ft.Row(
        [
            ft.Text("Soporte Técnico", size=26, weight="bold"),
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=volver_menu
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    layout = ft.Column(
        [
            header,
            ft.Divider(),
            ft.Row(
                [
                    panel_tickets,
                    panel_mensajeria
                ],
                expand=True,
                spacing=20
            )
        ],
        expand=True
    )
    page.add(layout)
    cargar_tickets()