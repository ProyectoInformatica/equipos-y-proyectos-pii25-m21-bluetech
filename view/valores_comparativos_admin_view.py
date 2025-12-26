import flet as ft

from controller.valores_comparativos_controller import (
    obtener_valores,
    actualizar_valores
)

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "black"


# =====================================================================
#  PANTALLA ADMIN: CONSULTAR / EDITAR PARÁMETROS DE SANIDAD
# =====================================================================

def mostrar_pantalla_parametros_sanidad(page: ft.Page, repo, usuario):

    from view.menu_admin_view import mostrar_pantalla_menu_admin

    page.clean()

    datos = obtener_valores()
    tarjetas = []

    def mostrar_error(mensaje):
        alerta = ft.AlertDialog(
            modal=True,
            title=ft.Text("❌ Error, el dato no es valido"),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: cerrar_alerta(alerta))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(alerta)
        alerta.open = True
        page.update()

    def cerrar_alerta(alerta):
        alerta.open = False
        page.update()

    def abrir_editor(categoria, subclave=None):

        if subclave:
            valores = datos[categoria][subclave]
            titulo = f"Editar {subclave}"
        else:
            valores = datos[categoria]
            titulo = f"Editar {categoria}"

        campos = {}
        controles = []

        for k, v in valores.items():
            campo = ft.TextField(label=k, value=str(v))
            campos[k] = campo
            controles.append(campo)

        def guardar_cambios(e):
            for clave, campo in campos.items():
                texto = campo.value.strip()

                if clave in ("min", "max"):
                    try:
                        valor = float(texto)
                    except ValueError:
                        mostrar_error(f"El campo '{clave}' debe ser un número.")
                        return

                    if valor < 0:
                        mostrar_error(f"El campo '{clave}' debe ser un número positivo.")
                        return
                else:
                    # Campos no numéricos (unidad, descripcion, etc.)
                    valor = texto

                if subclave:
                    datos[categoria][subclave][clave] = valor
                else:
                    datos[categoria][clave] = valor

            actualizar_valores(datos)
            dialog.open = False
            page.update()
            mostrar_pantalla_parametros_sanidad(page, repo, usuario)

        def cerrar_dialogo(e=None):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, size=20, weight="bold"),
            content=ft.Column(controles, tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.FilledButton("Guardar", on_click=guardar_cambios),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def make_on_click(categoria, subclave=None):
        return lambda e: abrir_editor(categoria, subclave)

    # ------------------- TARJETAS -------------------

    for categoria in ("temperatura", "humedad"):
        info = datos[categoria]

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
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            bgcolor=COLOR_PRINCIPAL,
                            color="white",
                            on_click=make_on_click(categoria),
                        ),
                    ]
                ),
            )
        )

    calidad = datos["calidad_aire"]
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
                        ft.Text(f"Máximo: {info['max']} {info['unidad']}"),
                        ft.Text(info["descripcion"], italic=True),
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            bgcolor=COLOR_PRINCIPAL,
                            color="white",
                            on_click=make_on_click("calidad_aire", subparam),
                        ),
                    ]
                ),
            )
        )

    boton_volver = ft.ElevatedButton(
        text="Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=COLOR_PRINCIPAL,
        color="white",
        on_click=lambda e: mostrar_pantalla_menu_admin(page, repo, usuario),
    )

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
                ft.Text("🔬 Parámetros de Sanidad", size=28, weight="bold", color=COLOR_PRINCIPAL),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PERSON, color="grey"), 
                        ft.Text(f" Usuario autenticado: {usuario.nombre_usuario}", size=14, italic=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,  # alinear texto al centro
                ),
                ft.Divider(),
                ft.Container(
                    expand=True,
                    content=ft.Column(controls=tarjetas, spacing=20, scroll=ft.ScrollMode.AUTO),
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
