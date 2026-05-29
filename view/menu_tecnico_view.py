import flet as ft
import asyncio
from view.grafico_consumo_dashboard import crear_panel_grafico_picos
from controller.ticket_controller import TicketController
from controller.mapa_habitaciones_controller import obtener_datos_mapa

# --- CONSTANTES DE ESTILO ---
COLOR_PRIMARIO = ft.Colors.BLUE_700
COLOR_BG = "#F0F2F5"
COLOR_SIDEBAR = ft.Colors.WHITE
COLOR_CHAT_BG = "#E5DDD5"

# --- COLORES MAPA ---
COLOR_DISPONIBLE = "#A8D5BA"
COLOR_OCUPADO = "#F2A2A2"
COLOR_ALERTA = "#FF0000"
COLOR_PASILLO = "#EDF2F7"


def mostrar_pantalla_menu_tecnico(page: ft.Page, repo, usuario):

    from view.login_view import mostrar_pantalla_login
    from view.alertas_sistema_view import mostrar_pantalla_alertas_sistema
    from view.alertas_usuario_tecnico_view import mostrar_pantalla_alertas_usuario
    from view.mapa_habitaciones_trabajadores_view import mostrar_pantalla_mapa_habitaciones_trabajadores

    page.clean()
    page.title = "BlueTech - Dashboard Técnico"
    page.bgcolor = COLOR_BG
    page.padding = 0

    controller = TicketController()

    ticket_actual = {"id": None, "data": None}

    # =========================
    # MAPA (MISMO QUE TRABAJADOR)
    # =========================
    habitaciones_parpadeo = []
    contenedor_mapa_vivo = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=20
    )

    def crear_habitacion_estilo_mapa(h_info, rangos):
        id_hab = h_info["id"]
        estado_db = h_info["estado"]
        temp = h_info["temperatura"]
        hum = h_info["humedad"]
        co2 = h_info["calidad_aire"].get("CO2", 0)

        r_temp = rangos.get("temperatura", {"min": 20, "max": 30})
        r_hum = rangos.get("humedad", {"min": 34, "max": 40})
        max_co2 = rangos.get("calidad_aire", {}).get("CO2", {}).get("max", 500)

        fuera_de_rango = (
            temp < r_temp["min"] or temp > r_temp["max"] or
            hum < r_hum["min"] or hum > r_hum["max"] or
            co2 > max_co2
        )

        color_base = COLOR_DISPONIBLE if not fuera_de_rango else COLOR_OCUPADO

        container_hab = ft.Container(
            content=ft.Column([
                ft.Text(f"{id_hab}", weight="bold", size=15),
                ft.Text(f"{temp}°C | {hum}%", size=10),
                ft.Row(
                    [ft.Icon(ft.Icons.AIR, size=10), ft.Text(f"{co2}", size=9)],
                    spacing=2
                ),
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
            width=115,
            height=90,
            bgcolor=color_base,
            border_radius=10,
            padding=8,
            data={"color_original": color_base}
        )

        if fuera_de_rango and estado_db == "ocupado":
            habitaciones_parpadeo.append(container_hab)

        return container_hab

    def reconstruir_mapa_dashboard():
        lista_hab, rangos = obtener_datos_mapa()

        habitaciones_parpadeo.clear()
        contenedor_mapa_vivo.controls.clear()

        num_plantas = (len(lista_hab) + 9) // 10

        for p in range(num_plantas):
            hab_planta = lista_hab[p * 10:(p + 1) * 10]

            fila_sup = ft.Row(spacing=12, alignment=ft.MainAxisAlignment.CENTER)
            fila_inf = ft.Row(spacing=12, alignment=ft.MainAxisAlignment.CENTER)

            for i, h in enumerate(hab_planta):
                (fila_sup if i < 5 else fila_inf).controls.append(
                    crear_habitacion_estilo_mapa(h, rangos)
                )

            pasillo = ft.Container(
                content=ft.Text(
                    f"PLANTA {p + 1}",
                    size=11,
                    weight="bold",
                    color="black45"
                ),
                bgcolor=COLOR_PASILLO,
                height=30,
                width=650,
                alignment=ft.Alignment(0, 0),
                border_radius=5
            )

            contenedor_mapa_vivo.controls.append(
                ft.Column(
                    [fila_sup, pasillo, fila_inf],
                    horizontal_alignment="center"
                )
            )

        page.update()

    # =========================
    # SIDEBAR
    # =========================
    def item_menu(icono, texto, seleccionado=False, accion=None):
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icono,
                                color=COLOR_PRIMARIO if seleccionado else ft.Colors.BLACK54),
                title=ft.Text(texto,
                              weight="bold" if seleccionado else "normal",
                              size=14),
                on_click=accion,
            ),
            bgcolor=ft.Colors.BLUE_50 if seleccionado else ft.Colors.TRANSPARENT,
            border_radius=10,
        )

    sidebar = ft.Container(
        width=280,
        bgcolor=COLOR_SIDEBAR,
        padding=30,
        content=ft.Column([
            ft.Row([
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON),
                    bgcolor=ft.Colors.BLUE_50,
                    radius=25
                ),
                ft.Column([
                    ft.Text(usuario.nombre_usuario, weight="bold"),
                    ft.Text("Técnico", color=ft.Colors.GREY_600, size=12)
                ], spacing=1)
            ], spacing=15),

            ft.Divider(height=40, color="transparent"),

            item_menu(ft.Icons.DASHBOARD_ROUNDED, "Dashboard", True),

            item_menu(
                ft.Icons.MAP_OUTLINED,
                "Mapa Hospital",
                False,
                lambda _: (
                    page.clean(),
                    mostrar_pantalla_mapa_habitaciones_trabajadores(page, repo, usuario, origen="tecnico")
                )
            ),

            item_menu(
                ft.Icons.DASHBOARD_CUSTOMIZE_OUTLINED,
                "Alertas Sistema",
                False,
                lambda _: (
                    page.clean(),
                    mostrar_pantalla_alertas_sistema(page, repo, usuario)
                )
            ),

            item_menu(
                ft.Icons.SUPPORT_AGENT,
                "Mis Notificaciones",
                False,
                lambda _: (
                    page.clean(),
                    mostrar_pantalla_alertas_usuario(page, repo, usuario)
                )
            ),

            ft.Container(expand=True),

            ft.TextButton(
                "Cerrar Sesión",
                icon=ft.Icons.LOGOUT,
                on_click=lambda _: (
                    setattr(usuario, "estado", 2),
                    repo.guardar_cambios(),
                    mostrar_pantalla_login(page, repo)
                ),
                style=ft.ButtonStyle(color="red")
            )
        ])
    )

    # =========================
    # TARJETA MAPA (ARRIBA)
    # =========================
    tarjeta_mapa = ft.Container(
        expand=True,
        bgcolor="white",
        border_radius=15,
        padding=25,
        shadow=ft.BoxShadow(blur_radius=15, color="black12"),
        content=ft.Column([
            ft.Row([
                ft.Text("Estado de Planta (Mapa en vivo)",
                        size=22,
                        weight="bold"),
                ft.IconButton(
                    ft.Icons.FULLSCREEN_ROUNDED,
                    on_click=lambda _: (
                        page.clean(),
                        mostrar_pantalla_mapa_habitaciones_trabajadores(page, repo, usuario, origen="tecnico")
                    )
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Divider(height=30),

            ft.Container(
                content=contenedor_mapa_vivo,
                expand=True
            )
        ])
    )

    # =========================
    # GRÁFICO INFERIOR
    # =========================
    grafico_metricas = crear_panel_grafico_picos(page, altura=220)

    tarjeta_inferior = ft.Container(
        height=305,
        bgcolor="white",
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color="black12"),
        content=ft.Column([
            ft.Text("Métricas y Estadísticas",
                    size=18,
                    weight="bold"),
            grafico_metricas
        ], spacing=12)
    )

    # =========================
    # PANEL PRINCIPAL
    # =========================
    panel_principal = ft.Container(
        expand=True,
        padding=30,
        content=ft.Column([
            ft.Text(
                f"Panel Operativo: {usuario.nombre_usuario}",
                size=24,
                weight="bold"
            ),
            tarjeta_mapa,
            tarjeta_inferior
        ], spacing=20)
    )

    # =========================
    # PARPADEO + ACTUALIZACIÓN
    # =========================
    async def parpadeo_dashboard():
        while True:
            try:
                if habitaciones_parpadeo:
                    for h in habitaciones_parpadeo:
                        h.bgcolor = COLOR_ALERTA
                    page.update()
                    await asyncio.sleep(0.5)

                    for h in habitaciones_parpadeo:
                        h.bgcolor = h.data["color_original"]
                    page.update()
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(1)
            except:
                break

    async def auto_actualizar():
        while True:
            try:
                await asyncio.sleep(5)
                reconstruir_mapa_dashboard()
            except:
                break

    # =========================
    # COMPOSICIÓN FINAL
    # =========================
    page.add(
        ft.Row([sidebar, panel_principal],
               expand=True,
               spacing=0)
    )

    reconstruir_mapa_dashboard()
    page.run_task(parpadeo_dashboard)
    page.run_task(auto_actualizar)