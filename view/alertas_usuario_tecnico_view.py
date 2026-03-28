import flet as ft
from controller.alertas_usuario_controller import AlertasUsuarioController

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    page.clean()
    page.bgcolor = "#f5f7fa"

    controller = AlertasUsuarioController()
    ticket_actual = {"id": None, "data": None}
    mensajes_column = ft.Column(scroll="auto", expand=True)
    tickets_column = ft.Column(scroll="auto", expand=True)
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True
    )
    boton_asignar = ft.ElevatedButton(
        "Asignarme ticket",
        visible=False
    )

    # VOLVER
    def volver_menu(e):
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    # CARGAR MENSAJES
    def cargar_mensajes(id_alerta):
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_alerta)
        for m in mensajes:
            es_tecnico = m["rol"] == "tecnico"
            mensaje = ft.Row(
                alignment=ft.MainAxisAlignment.END if es_tecnico else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=350,  
                        bgcolor="#d2f8d2" if es_tecnico else "#e9f5ff",
                        padding=10,
                        border_radius=ft.border_radius.only(
                            top_left=10,
                            top_right=10,
                            bottom_left=10 if es_tecnico else 0,
                            bottom_right=0 if es_tecnico else 10
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
        ticket_actual["data"] = alerta
        if alerta["estado"] == "pendiente":
            boton_asignar.visible = True
        else:
            boton_asignar.visible = False
        cargar_mensajes(alerta["id_alerta"])
        page.update()

    # CARGAR TICKETS
    def cargar_tickets():
        tickets_column.controls.clear()
        alertas = controller.obtener_alertas()
        for alerta in alertas:
            if alerta["estado"] == "pendiente" or alerta.get("id_tecnico") == usuario.id_usuario:
                ticket = ft.ListTile(
                    title=ft.Text(alerta["descripcion"]),
                    subtitle=ft.Text(
                        f"Estado: {alerta['estado']} - {alerta['nombre_emisor']}"
                    ),
                    on_click=lambda e, a=alerta: seleccionar_ticket(a)
                )
                tickets_column.controls.append(ticket)
        page.update()

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

    # ASIGNAR TICKET
    def asignarme_ticket(e):
        if ticket_actual["id"] is None:
            return
        res = controller.asignar_ticket(ticket_actual["id"], usuario)
        cargar_tickets()
        boton_asignar.visible = False
        page.update()
    boton_asignar.on_click = asignarme_ticket

    # PANEL TICKETS
    panel_tickets = ft.Container(
        expand=1,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            [
                ft.Text("Tickets disponibles", size=22, weight="bold"),
                ft.Divider(),
                tickets_column
            ]
        )
    )

    # PANEL MENSAJERIA
    panel_mensajeria = ft.Container(
        expand=3,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            [
                ft.Text("Conversación del ticket", size=22, weight="bold"),
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
                ),
                boton_asignar
            ],
            expand=True
        )
    )

    # HEADER
    header = ft.Row(
        [
            ft.Text("Gestión de Tickets", size=26, weight="bold"),
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