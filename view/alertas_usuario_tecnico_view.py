import flet as ft
from controller.alertas_usuario_controller import AlertasUsuarioController

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    page.clean()
    page.bgcolor = "#F0F2F5"
    controller = AlertasUsuarioController()
    ticket_actual = {"id": None, "data": None}
    
    #--- Componentes de la interfaz ---
    mensajes_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    tickets_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True,
        border_radius=25,
        on_submit=lambda e: enviar_mensaje(e),
        bgcolor=ft.Colors.GREY_50
    )
    boton_asignar = ft.ElevatedButton(
        "Asignarme ticket",
        icon=ft.Icons.ASSIGNMENT_IND,
        visible=False,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
    )

    def volver_menu(e):
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    #--- Lógica de Mensajes ---
    def cargar_mensajes(id_alerta):
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_alerta)
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
        #Auto-scroll al último mensaje
        mensajes_column.scroll_to(offset=-1, duration=500)

    def seleccionar_ticket(alerta):
        ticket_actual["id"] = alerta["id_alerta"]
        ticket_actual["data"] = alerta
        boton_asignar.visible = (alerta["estado"] == "pendiente")
        cargar_mensajes(alerta["id_alerta"])

    def cargar_tickets():
        tickets_column.controls.clear()
        alertas = controller.obtener_alertas()
        for alerta in alertas:
            #Mostramos pendientes o los que ya tiene el técnico
            if alerta["estado"] == "pendiente" or alerta.get("id_tecnico") == usuario.id_usuario:
                tickets_column.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CONFIRMATION_NUMBER_OUTLINED),
                        title=ft.Text(alerta["descripcion"], weight=ft.FontWeight.W_500),
                        subtitle=ft.Text(f"{alerta['nombre_emisor']} • {alerta['estado']}"),
                        on_click=lambda e, a=alerta: seleccionar_ticket(a),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                )
        page.update()

    def enviar_mensaje(e):
        if not ticket_actual["id"] or not input_mensaje.value.strip():
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        input_mensaje.focus()
        cargar_mensajes(ticket_actual["id"])

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
            ], spacing=10),
            ft.Container(boton_asignar, alignment=ft.alignment.center, padding=10)
        ])
    )

    page.add(
        ft.Column([
            ft.Row([
                ft.Text("Gestión de Tickets", size=28, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=volver_menu, icon_color="red")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([panel_tickets, panel_mensajeria], expand=True, spacing=15)
        ], expand=True, padding=10)
    )

    cargar_tickets()