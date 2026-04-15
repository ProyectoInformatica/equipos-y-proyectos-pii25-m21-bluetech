import flet as ft
import asyncio
from controller.ticket_controller import TicketController
#from view.grafico_consumo_dashboard import crear_panel_grafico_picos

# --- CONSTANTES DE ESTILO ---
COLOR_PRIMARIO = ft.Colors.BLUE_700
COLOR_BG = "#F0F2F5"
COLOR_SIDEBAR = ft.Colors.WHITE
COLOR_CHAT_BG = "#E5DDD5" 

def mostrar_pantalla_menu_tecnico(page: ft.Page, repo, usuario):
    from view.login_view import mostrar_pantalla_login
    from view.alertas_sistema_view import mostrar_pantalla_alertas_sistema
    from view.alertas_usuario_tecnico_view import mostrar_pantalla_alertas_usuario
    
    page.clean()
    page.title = "BlueTech - Dashboard Técnico"
    page.bgcolor = COLOR_BG
    page.padding = 0

    controller = TicketController()
    ticket_actual = {"id": None, "data": None}

    # --- COMPONENTES DEL CHAT (Tu lógica) ---
    mensajes_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    tickets_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    input_mensaje = ft.TextField(
        hint_text="Escribe un mensaje...",
        expand=True,
        border_radius=25,
        bgcolor=ft.Colors.GREY_50,
        text_size=13,
        on_submit=lambda e: page.run_task(enviar_mensaje_task)
    )

    boton_asignar = ft.ElevatedButton(
        "Asignarme este ticket",
        icon=ft.Icons.ASSIGNMENT_IND,
        visible=False,
        on_click=lambda e: asignarme_ticket_logic(),
        style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color=ft.Colors.WHITE)
    )

    # --- FUNCIONES DE LÓGICA (Sockets + UI) ---
    async def cargar_mensajes(id_ticket):
        mensajes_column.controls.clear()
        mensajes = controller.obtener_mensajes(id_ticket)
        for m in mensajes:
            es_tecnico = m["rol"] == "tecnico"
            mensajes_column.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.END if es_tecnico else ft.MainAxisAlignment.START,
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                ft.Text(m["nombre_emisor"], size=10, weight="bold", color=ft.Colors.BLUE_700),
                                ft.Text(m["texto"], size=13),
                                ft.Text(m["fecha_hora"], size=9, color=ft.Colors.GREY_600),
                            ], spacing=2, tight=True),
                            bgcolor="#DCF8C6" if es_tecnico else ft.Colors.WHITE,
                            padding=12,
                            border_radius=ft.border_radius.only(
                                top_left=12, top_right=12, 
                                bottom_left=12 if es_tecnico else 2, 
                                bottom_right=2 if es_tecnico else 12
                            ),
                            width=280,
                        )
                    ]
                )
            )
        page.update()
        # --- AUTO-SCROLL AL FINAL ---
        await asyncio.sleep(0.1) 
        await mensajes_column.scroll_to(offset=-1, duration=500, curve=ft.AnimationCurve.DECELERATE)

    async def seleccionar_ticket(ticket):
        ticket_actual["id"] = ticket["id_ticket"]
        ticket_actual["data"] = ticket
        boton_asignar.visible = (ticket["estado"] == "pendiente")
        await cargar_mensajes(ticket["id_ticket"])
        actualizar_input_bar()
        page.update()

    def cargar_tickets():
        tickets_column.controls.clear()
        tickets = controller.obtener_tickets()
        for t in tickets:
            # Solo mostramos pendientes o los que ya tiene este técnico
            if t["estado"] != "cerrado" and (t["estado"] == "pendiente" or t.get("id_tecnico") == usuario.id_usuario):
                tickets_column.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.CONFIRMATION_NUMBER_OUTLINED, color=COLOR_PRIMARIO),
                            title=ft.Text(t["descripcion"], size=13, weight="bold", max_lines=1),
                            subtitle=ft.Text(f"{t['nombre_emisor']} • {t['estado']}", size=11),
                            on_click=lambda e, sel=t: page.run_task(seleccionar_ticket, sel),
                        ),
                        border_radius=10,
                        margin=ft.margin.only(bottom=5),
                        bgcolor=ft.Colors.GREY_50
                    )
                )
        page.update()

    async def enviar_mensaje_task(e=None):
        if not ticket_actual["id"] or not input_mensaje.value.strip():
            return
        if ticket_actual["data"].get("id_tecnico") != usuario.id_usuario:
            page.snack_bar = ft.SnackBar(
                ft.Text("Debes asignarte el ticket antes de responder")
            )
            page.snack_bar.open = True
            page.update()
            return
        if ticket_actual["data"]["estado"] == "cerrado":
            return
        controller.enviar_mensaje(usuario, ticket_actual["id"], input_mensaje.value.strip())
        input_mensaje.value = ""
        page.update()
        await cargar_mensajes(ticket_actual["id"])

    def asignarme_ticket_logic():
        if ticket_actual["id"]:
            controller.asignar_ticket(ticket_actual["id"], usuario)
            ticket_actual["data"]["id_tecnico"] = usuario.id_usuario
            cargar_tickets()
            boton_asignar.visible = False
            actualizar_input_bar()
            page.update()

    input_row = ft.Container()
    def actualizar_input_bar():
        if not ticket_actual["data"]:
            input_row.content = ft.Text("Selecciona un ticket")
        elif ticket_actual["data"].get("id_tecnico") != usuario.id_usuario:
            input_row.content = ft.Text(
                "⚠️ Debes asignarte este ticket para responder",
                color=ft.Colors.ORANGE_700
            )
        else:
            input_row.content = ft.Row([
                input_mensaje,
                ft.IconButton(
                    ft.Icons.SEND_ROUNDED,
                    icon_color=COLOR_PRIMARIO,
                    on_click=lambda e: page.run_task(enviar_mensaje_task)
                )
            ])
        page.update()

    # --- ESTRUCTURA SIDEBAR ---
    def item_menu(icono, texto, seleccionado=False, accion=None):
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icono, color=COLOR_PRIMARIO if seleccionado else ft.Colors.BLACK54),
                title=ft.Text(texto, weight="bold" if seleccionado else "normal", size=14),
                on_click=accion,
            ),
            bgcolor=ft.Colors.BLUE_50 if seleccionado else ft.Colors.TRANSPARENT,
            border_radius=10,
        )

    sidebar = ft.Container(
        width=280, bgcolor=COLOR_SIDEBAR, padding=30,
        content=ft.Column([
            ft.Row([
                ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON), bgcolor=ft.Colors.BLUE_50, radius=25),
                ft.Column([
                    ft.Text(usuario.nombre_usuario, weight="bold"),
                    ft.Text("Técnico", color=ft.Colors.GREY_600, size=12)
                ], spacing=1)
            ], spacing=15),
            ft.Divider(height=40, color="transparent"),
            item_menu(ft.Icons.DASHBOARD_ROUNDED, "Dashboard", True),
            item_menu(ft.Icons.DASHBOARD_CUSTOMIZE_OUTLINED, "Alertas Sistema", False, 
                    lambda _: (page.clean(), mostrar_pantalla_alertas_sistema(page, repo, usuario))),
            item_menu(ft.Icons.SUPPORT_AGENT, "Mis Notificaciones", False,
                    lambda _: (page.clean(), mostrar_pantalla_alertas_usuario(page, repo, usuario))),
            ft.Container(expand=True),
            ft.TextButton("Cerrar Sesión", icon=ft.Icons.LOGOUT, on_click=lambda _: (setattr(usuario, 'estado', 2), repo.guardar_cambios(), mostrar_pantalla_login(page, repo)), style=ft.ButtonStyle(color="red"))
        ])
    )

    # --- PANEL DE COMUNICACIÓN INTEGRADO ---
    tarjeta_comunicaciones = ft.Container(
        expand=True, bgcolor="white", border_radius=15, padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color="black12"),
        content=ft.Row([
            # Sub-panel Izquierdo: Lista de Tickets
            ft.Container(
                width=250,
                content=ft.Column([
                    ft.Text("Tickets Disponibles", weight="bold", size=16),
                    ft.Divider(),
                    tickets_column
                ])
            ),
            ft.VerticalDivider(width=1),
            # Sub-panel Derecho: Chat
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Chat de Soporte", weight="bold", size=16),
                        boton_asignar
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=mensajes_column, 
                        expand=True, 
                        width=1000,
                        bgcolor=COLOR_CHAT_BG, 
                        border_radius=10, 
                        padding=15
                    ),
                    input_row
                ])
            )
        ], spacing=20)
    )

    #grafico_metricas = crear_panel_grafico_picos(page, altura=205)
    # --- GRÁFICO (Placeholder) ---
    tarjeta_inferior = ft.Container(
        height=285,
        bgcolor="white",
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color="black12"),
        content=ft.Column(
            [
                ft.Text("Métricas y Estadísticas", size=18, weight="bold"),
                #grafico_metricas
            ],
            spacing=12
        )
    )

    # --- COMPOSICIÓN FINAL ---
    page.add(
        ft.Row([
            sidebar,
            ft.Container(
                expand=True, padding=30,
                content=ft.Column([
                    ft.Text(f"Panel Operativo: {usuario.nombre_usuario}", size=24, weight="bold"),
                    tarjeta_comunicaciones,
                    tarjeta_inferior
                ], spacing=20)
            )
        ], expand=True, spacing=0)
    )

    # Inicializar datos
    cargar_tickets()