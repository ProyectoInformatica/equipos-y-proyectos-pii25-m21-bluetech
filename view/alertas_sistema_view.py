import flet as ft
from controller.ticket_controller import TicketController


def mostrar_pantalla_alertas_sistema(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    page.clean()
    controller = TicketController()
    page.bgcolor = "#F5F7FA"

    # COLUMNAS POR SENSOR
    col_temperatura = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    col_humedad = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    col_otros = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def cerrar_sesion(e):
        usuario.estado = 2
        repo.guardar_cambios()
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    def asignar(tid):
        controller.tomar_ticket(tid, usuario.id_usuario, usuario.nombre_usuario)
        refrescar_tickets()

    def desasignar(tid):
        controller.desasignar_ticket(tid, usuario.id_usuario)
        refrescar_tickets()

    def cerrar(tid):
        controller.finalizar_ticket(tid, usuario.id_usuario)
        refrescar_tickets()

    def estado_chip(estado):
        if estado == "pendiente":
            return ft.Container(
                bgcolor="#ffebee",
                padding=ft.padding.symmetric(6, 3),
                border_radius=20,
                content=ft.Text("PENDIENTE", color="red", size=11, weight="bold")
            )
        return ft.Container(
            bgcolor="#e3f2fd",
            padding=ft.padding.symmetric(6, 3),
            border_radius=20,
            content=ft.Text("EN PROCESO", color="blue", size=11, weight="bold")
        )

    def crear_card_ticket(t):
        fila_acciones = ft.Row(spacing=10)
        id_asignado = t.get("tecnico_id")
        nombre_asignado = t.get("tecnico_nombre", "Desconocido")
        info_tecnico_ui = ft.Container()
        if t["estado"] == "pendiente":
            fila_acciones.controls.append(
                ft.ElevatedButton(
                    "Atender",
                    icon=ft.Icons.PLAY_ARROW,
                    bgcolor="#1976D2",
                    color="white",
                    on_click=lambda e, tid=t["id_ticket"]: asignar(tid)
                )
            )
        elif t["estado"] == "en_proceso":
            if id_asignado == usuario.id_usuario:
                info_tecnico_ui = ft.Text(
                    f"Asignado a ti ({usuario.nombre_usuario})",
                    color="green",
                    weight="bold"
                )
                fila_acciones.controls.extend([
                    ft.ElevatedButton(
                        "Finalizar",
                        icon=ft.Icons.CHECK,
                        bgcolor="green",
                        color="white",
                        on_click=lambda e, tid=t["id_ticket"]: cerrar(tid)
                    ),
                    ft.OutlinedButton(
                        "Soltar",
                        icon=ft.Icons.UNDO,
                        on_click=lambda e, tid=t["id_ticket"]: desasignar(tid)
                    )
                ])
            else:
                info_tecnico_ui = ft.Text(
                    f"Técnico: {nombre_asignado}",
                    color="orange"
                )
        return ft.Container(
            bgcolor="white",
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(
                blur_radius=12,
                color="#E0E0E0"
            ),
            content=ft.Column([
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Ticket #{t['id_ticket']}",
                                    weight="bold",
                                    size=16
                                ),
                                ft.Text(
                                    f"Habitación {t['id_habitacion']}",
                                    size=12,
                                    color="grey"
                                )
                            ],
                            spacing=2
                        ),
                        estado_chip(t["estado"])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text(f"Sensor: {t['tipo_sensor']}"),
                ft.Text(f"Valor: {t['valor_detectado']}", weight="bold"),
                ft.Text(f"Límite: {t['limite_establecido']}"),
                ft.Text(t["descripcion"], size=12),
                info_tecnico_ui,
                ft.Divider(),
                fila_acciones,
                ft.Text(t["fecha"], size=10, color="grey")
            ], spacing=6)
        )

    def refrescar_tickets():
        col_temperatura.controls.clear()
        col_humedad.controls.clear()
        col_otros.controls.clear()
        tickets = controller.obtener_pendientes()
        for t in tickets:
            card = crear_card_ticket(t)
            tipo = t["tipo_sensor"].lower()
            if "temperatura" in tipo:
                col_temperatura.controls.append(card)
            elif "humedad" in tipo:
                col_humedad.controls.append(card)
            else:
                col_otros.controls.append(card)
        page.update()

    # CABECERAS DE SECTOR
    sector_temperatura = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.THERMOSTAT, color="red"),
                ft.Text("Temperatura", weight="bold", size=18)
            ]),
            ft.Divider(),
            col_temperatura
        ])
    )
    sector_humedad = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.WATER_DROP, color="blue"),
                ft.Text("Humedad", weight="bold", size=18)
            ]),
            ft.Divider(),
            col_humedad
        ])
    )
    sector_otros = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SENSORS, color="purple"),
                ft.Text("Otros sensores", weight="bold", size=18)
            ]),
            ft.Divider(),
            col_otros
        ])
    )

    header = ft.Row(
        [
            ft.Text(
                f"Panel Técnico - {usuario.nombre_usuario}",
                size=24,
                weight="bold"
            ),
            ft.Row([
                ft.IconButton(
                    ft.Icons.REFRESH,
                    on_click=lambda _: refrescar_tickets()
                ),
                ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=cerrar_sesion
                )
            ])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.add(
        ft.Column(
            [
                header,
                ft.Divider(),
                ft.Row(
                    [
                        sector_temperatura,
                        sector_humedad,
                        sector_otros
                    ],
                    expand=True,
                    spacing=20
                )
            ],
            expand=True
        )
    )
    refrescar_tickets()