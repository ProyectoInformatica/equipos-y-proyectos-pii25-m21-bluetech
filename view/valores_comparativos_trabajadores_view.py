import flet as ft
from controller.valores_comparativos_controller import obtener_valores

COLOR_PRINCIPAL = "blue"


def mostrar_pantalla_parametros_sanidad_trabajador(page: ft.Page, repo, usuario):

    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    page.clean()

    # 🔹 SOLO lectura desde controller
    datos = obtener_valores()
    tarjetas = []

    # ------------------- TARJETAS -------------------

    # Temperatura y humedad
    for categoria in ("temperatura", "humedad"):
        info = datos.get(categoria, {})

        tarjetas.append(
            ft.Container(
                width=650,
                bgcolor="white",
                padding=15,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=8, color="grey"),
                margin=ft.margin.symmetric(horizontal=10, vertical=10),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{'🌡️' if categoria == 'temperatura' else '💧'} {categoria.capitalize()}",
                            size=20,
                            weight="bold",
                            color=COLOR_PRINCIPAL,
                        ),
                        ft.Text(
                            f"Rango: {info.get('min')} - {info.get('max')} {info.get('unidad')}"
                        ),
                        ft.Text(info.get("descripcion", ""), italic=True),
                        # ❌ SIN botón editar
                    ]
                ),
            )
        )

    # Calidad del aire
    calidad = datos.get("calidad_aire", {})
    for subparam, info in calidad.items():
        tarjetas.append(
            ft.Container(
                width=650,
                bgcolor="white",
                padding=15,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=8, color="grey"),
                margin=ft.margin.symmetric(horizontal=10, vertical=10),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"🫁 {subparam}",
                            size=20,
                            weight="bold",
                            color=COLOR_PRINCIPAL,
                        ),
                        ft.Text(f"Máximo: {info.get('max')} {info.get('unidad')}"),
                        ft.Text(info.get("descripcion", ""), italic=True),
                        # ❌ SIN botón editar
                    ]
                ),
            )
        )

    # ------------------- BOTÓN VOLVER -------------------

    boton_volver = ft.ElevatedButton(
        text="Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=COLOR_PRINCIPAL,
        color="white",
        on_click=lambda e: mostrar_pantalla_menu_trabajador(page, repo, usuario),
    )

    # ------------------- CONTENEDOR PRINCIPAL -------------------

    tarjeta = ft.Container(
        width=750,
        height=600,
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        content=ft.Column(
            spacing=25,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                ft.Text(
                    "🔬 Parámetros de Sanidad",
                    size=28,
                    weight="bold",
                    color=COLOR_PRINCIPAL,
                ),
                ft.Divider(),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        controls=tarjetas,
                        spacing=20,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
                ft.Divider(),
                boton_volver,
            ],
        ),
    )

    page.add(
        ft.Stack(
            expand=True,
            controls=[
                ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
                ft.Container(expand=True, alignment=ft.alignment.center, content=tarjeta),
            ],
        )
    )

    page.update()