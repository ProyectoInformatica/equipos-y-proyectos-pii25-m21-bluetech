import flet as ft
import json

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "black"

def mostrar_pantalla_parametros_sanidad_trabajador(page: ft.Page, repo, usuario):

    # IMPORTACIÓN CORRECTA PARA EL MENÚ DE TRABAJADOR
    from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    # Limpiar pantalla
    page.clean()

    # Cargar valores desde el JSON
    try:
        with open("valores_comparativos.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except Exception as e:
        page.add(ft.Text(f"Error al cargar valores_comparativos.json: {e}", color="red"))
        return

    # Crear listas de tarjetas visuales
    tarjetas_parametros = []

    # ---- TEMPERATURA ----
    temp = datos.get("temperatura", {})
    tarjetas_parametros.append(
        ft.Container(
            bgcolor="white",
            padding=15,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=8, color="grey"),
            content=ft.Column([
                ft.Text("🌡️ Temperatura", size=20, weight="bold", color=COLOR_PRINCIPAL),
                ft.Text(f"Rango: {temp.get('min')} - {temp.get('max')} {temp.get('unidad')}"),
                ft.Text(temp.get("descripcion", ""), italic=True)
            ])
        )
    )

    # ---- HUMEDAD ----
    hum = datos.get("humedad", {})
    tarjetas_parametros.append(
        ft.Container(
            bgcolor="white",
            padding=15,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=8, color="grey"),
            content=ft.Column([
                ft.Text("💧 Humedad", size=20, weight="bold", color=COLOR_PRINCIPAL),
                ft.Text(f"Rango: {hum.get('min')} - {hum.get('max')} {hum.get('unidad')}"),
                ft.Text(hum.get("descripcion", ""), italic=True)
            ])
        )
    )

    # ---- CALIDAD DEL AIRE ----
    calidad = datos.get("calidad_aire", {})
    for clave, info in calidad.items():
        tarjetas_parametros.append(
            ft.Container(
                bgcolor="white",
                padding=15,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=8, color="grey"),
                content=ft.Column([
                    ft.Text(f"🫁 {clave}", size=20, weight="bold", color=COLOR_PRINCIPAL),
                    ft.Text(f"Límite máximo: {info.get('max')} {info.get('unidad')}"),
                    ft.Text(info.get("descripcion", ""), italic=True)
                ])
            )
        )

    # Botón para volver (versión trabajador)
    boton_volver = ft.ElevatedButton(
        text="Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=COLOR_PRINCIPAL,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: mostrar_pantalla_menu_trabajador(page, repo, usuario)
    )

    # Tarjeta contenedora central
    tarjeta_principal = ft.Container(
        width=700,
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        content=ft.Column(
            controls=[
                ft.Text("🔬 Parámetros de Sanidad", size=28, weight="bold", color=COLOR_PRINCIPAL),
                ft.Text(f"Usuario autenticado: {usuario.nombre_usuario}", size=14, italic=True, color="grey"),
                ft.Divider(),
                ft.Column(tarjetas_parametros, spacing=20),
                ft.Divider(),
                boton_volver
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25
        )
    )

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                alignment=ft.alignment.center,
                content=tarjeta_principal,
                expand=True
            )
        ]
    )

    page.add(layout)
    page.update()
