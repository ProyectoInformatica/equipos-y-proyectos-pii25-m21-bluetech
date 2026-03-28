import flet as ft


def mostrar_pantalla_alertas_usuario(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    page.clean()
    page.bgcolor = "#f5f7fa"

    def volver_menu(e):
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    # PANEL TICKETS (25%)
    panel_tickets = ft.Container(
        expand=1,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "Tickets:",
                    size=22,
                    weight="bold"
                ),
                ft.Divider(),
                ft.Text(
                    "Aquí aparecerán los tickets de usuarios",
                    size=16,
                    color="grey"
                )
            ],
            spacing=10
        )
    )

    # PANEL MENSAJERIA (75%)
    panel_mensajeria = ft.Container(
        expand=3,
        bgcolor="white",
        border_radius=10,
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "Conversación del ticket:",
                    size=22,
                    weight="bold"
                ),
                ft.Divider(),
                ft.Text(
                    "Aquí aparecerá el sistema de mensajería",
                    size=16,
                    color="grey"
                )
            ],
            spacing=10
        )
    )

    # HEADER
    header = ft.Row(
        [
            ft.Text(
                "Alertas de Usuario",
                size=26,
                weight="bold"
            ),
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Volver",
                on_click=volver_menu
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # LAYOUT PRINCIPAL
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
        expand=True,
        spacing=20
    )
    page.add(layout)
    page.update()