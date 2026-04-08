import flet as ft

def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    
    page.clean()
    page.bgcolor = "#F0F2F5" 

    def volver_menu(e):
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    #PANEL TICKETS (25%)
    panel_tickets = ft.Container(
        expand=1,
        bgcolor=ft.Colors.WHITE,
        border_radius=15, 
        padding=25,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.05, "black"),
            spread_radius=1
        ),
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.BLUE_700),
                    ft.Text("Tickets", size=22, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(height=20, thickness=1),
                ft.Container(
                    content=ft.Text(
                        "Aquí aparecerán los tickets de usuarios",
                        size=14,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            spacing=10
        )
    )

    #PANEL MENSAJERIA (75%)
    panel_mensajeria = ft.Container(
        expand=3,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=25,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.05, "black"),
            spread_radius=1
        ),
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=ft.Colors.BLUE_700),
                    ft.Text("Conversación del ticket", size=22, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(height=20, thickness=1),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FORUM_OUTLINED, size=50, color=ft.Colors.GREY_300),
                        ft.Text(
                            "Selecciona un ticket para ver la conversación",
                            size=16,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            spacing=10
        )
    )

    #HEADER
    header = ft.Row(
        [
            ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.Colors.BLUE_700, size=30),
                ft.Text(
                    "Alertas de Usuario",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_800
                ),
            ], spacing=15),
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW, 
                tooltip="Volver al menú principal",
                icon_color=ft.Colors.BLUE_GREY_700,
                on_click=volver_menu,
                style=ft.ButtonStyle(
                    shape=ft.CircleBorder(),
                )
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    #LAYOUT PRINCIPAL
    layout = ft.Column(
        [
            header,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row(
                [
                    panel_tickets,
                    panel_mensajeria
                ],
                expand=True,
                spacing=25
            )
        ],
        expand=True,
        spacing=0 
    )

    page.add(
        ft.Container(layout, padding=20, expand=True)
    )
    page.update()