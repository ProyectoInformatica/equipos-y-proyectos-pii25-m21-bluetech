import flet as ft
from controller.alerta_controller import AlertaController

def mostrar_pantalla_alertas_sistema(page: ft.Page, repo, usuario):
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico
    
    page.controls.clear()
    controller = AlertaController()
    page.bgcolor = "#F5F7FA"

    #--- Columnas por Sensor ---
    col_temperatura = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    col_humedad = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
    col_otros = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)

    #--- Funciones de acciones ---
    def cerrar_sesion(e):
        usuario.estado = 2
        repo.guardar_cambios()
        mostrar_pantalla_menu_tecnico(page, repo, usuario)

    def asignar(tid):
        controller.tomar_ticket(tid, usuario.id_usuario, usuario.nombre_usuario)
        refrescar_tickets()

    def desasignar(tid):
        controller.desasignar_ticket(tid)
        refrescar_tickets()

    def cerrar(tid):
        controller.finalizar_ticket(tid, usuario.id_usuario, usuario.nombre_usuario)
        refrescar_tickets()

    def estado_chip(estado):
        es_pendiente = estado == "Pendiente"
        return ft.Container(
            bgcolor="#ffebee" if es_pendiente else "#e3f2fd",
            padding=ft.padding.symmetric(vertical=6, horizontal=12),
            border_radius=20,
            content=ft.Text(
                "PENDIENTE" if es_pendiente else "EN PROCESO",
                color="red" if es_pendiente else "blue",
                size=11,
                weight=ft.FontWeight.BOLD
            )
        )

    def crear_card_ticket(t):
        fila_acciones = ft.Row(spacing=10)
        id_asignado = t.get("tecnico_id")
        nombre_asignado = t.get("tecnico_nombre", "Desconocido")
        info_tecnico_ui = ft.Container()
        limite_texto = f"{t['limite_min']} - {t['limite_max']}" if t['limite_min'] else f"Max: {t['limite_max']}"

        if t["estado"] == "Pendiente":
            fila_acciones.controls.append(
                ft.ElevatedButton(
                    content=ft.Text("Atender", color="white"),
                    icon=ft.Icons.PLAY_ARROW,
                    style=ft.ButtonStyle(bgcolor="#1976D2"),
                    on_click=lambda e, tid=t["id_alerta"]: asignar(tid)
                )
            )
        elif t["estado"] == "En_Proceso":
            if id_asignado == usuario.id_usuario:
                info_tecnico_ui = ft.Text(
                    "Asignado a ti",
                    color=ft.Colors.GREEN_700,
                    weight=ft.FontWeight.BOLD
                )
                fila_acciones.controls.extend([
                    ft.ElevatedButton(
                        content=ft.Text("Finalizar", color="white"),
                        icon=ft.Icons.CHECK,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700),
                        on_click=lambda e, tid=t["id_alerta"]: cerrar(tid)
                    ),
                    ft.OutlinedButton(
                        content=ft.Text("Soltar"),
                        icon=ft.Icons.UNDO,
                        on_click=lambda e, tid=t["id_alerta"]: desasignar(tid)
                    )
                ])
            else:
                info_tecnico_ui = ft.Text(
                    f"Técnico: {nombre_asignado}",
                    color=ft.Colors.ORANGE_800
                )

        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black")),
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Column([
                            ft.Text(f"Alerta #{t['id_alerta']}", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"Habitación {t['id_habitacion']}", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"Sensor ID {t['id_sensor']}", size=12, color=ft.Colors.GREY_600)
                        ], spacing=2),
                        estado_chip(t["estado"])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Sensor {t['tipo_sensor']}"),
                    ft.Text(f"Valor: {t['valor_detectado']}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Limites establecidos: {[limite_texto]}"),
                    ft.Text(t["descripcion"], size=12, italic=True),
                    info_tecnico_ui,
                    ft.Divider(height=10, thickness=1),
                    fila_acciones,
                    ft.Text(t["fecha"], size=10, color=ft.Colors.GREY_400)
                ],
                spacing=8
            )
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

    #--- UI estática ---
    def crear_sector(titulo, icono, color_icono, columna):
        return ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Icon(icono, color=color_icono),
                    ft.Text(titulo, weight=ft.FontWeight.BOLD, size=18)
                ]),
                ft.Divider(color=color_icono),
                columna
            ])
        )

    header = ft.Row(
        [
            ft.Text(f"Panel Técnico - {usuario.nombre_usuario}", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: refrescar_tickets(), tooltip="Refrescar"),
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=cerrar_sesion, tooltip="Volver")
            ])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.add(
        ft.Column([
            header,
            ft.Divider(),
            ft.Row([
                crear_sector("Temperatura", ft.Icons.THERMOSTAT, ft.Colors.RED, col_temperatura),
                crear_sector("Humedad", ft.Icons.WATER_DROP, ft.Colors.BLUE, col_humedad),
                crear_sector("Otros", ft.Icons.SENSORS, ft.Colors.PURPLE, col_otros),
            ], expand=True, spacing=20)
        ], expand=True)
    )

    #Carga inicial
    refrescar_tickets()