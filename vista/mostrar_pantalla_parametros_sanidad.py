import flet as ft
import json

RUTA_JSON = "valores_comparativos.json"

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "black"


# ---------------------- UTILIDADES JSON ---------------------- #

def cargar_valores():
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_valores(data):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =====================================================================
#  PANTALLA ADMIN: CONSULTAR / EDITAR PARÁMETROS DE SANIDAD
# =====================================================================

def mostrar_pantalla_parametros_sanidad(page: ft.Page, repo, usuario):

    from vista.menu_admin_view import mostrar_pantalla_menu_admin

    page.clean()

    datos = cargar_valores()
    tarjetas = []

    # ---------- FUNCIÓN PARA ABRIR EL DIÁLOGO DE EDICIÓN ----------

    def abrir_editor(categoria, subclave=None):

        # Obtener el diccionario que se va a editar
        if subclave:
            valores = datos[categoria][subclave]
            titulo = f"Editar {subclave}"
        else:
            valores = datos[categoria]
            titulo = f"Editar {categoria}"

        # Crear campos dinámicamente
        campos = {}
        controles = []

        for k, v in valores.items():
            campo = ft.TextField(label=k, value=str(v))
            campos[k] = campo
            controles.append(campo)

        # Función guardar cambios
        def guardar_cambios(e):
            for clave, campo in campos.items():
                texto = campo.value.strip()

                # Convertir a número si es posible (decimales positivos)
                if texto.replace(".", "", 1).isdigit():
                    valor = float(texto)
                else:
                    valor = texto

                if subclave:
                    datos[categoria][subclave][clave] = valor
                else:
                    datos[categoria][clave] = valor

            guardar_valores(datos)
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

    # Handler para botones (para evitar problemas de closure en bucles)
    def make_on_click(categoria, subclave=None):
        def handler(e):
            abrir_editor(categoria, subclave)
        return handler

    # ------------------- CREACIÓN DE TARJETAS DE DATOS -------------------

    # Temperatura y humedad
    for categoria in ("temperatura", "humedad"):
        info = datos[categoria]

        tarjetas.append(
            ft.Container(
                width=650,                         # mismo ancho para todas
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

    # Calidad del aire (subparámetros)
    calidad = datos["calidad_aire"]
    for subparam, info in calidad.items():
        tarjetas.append(
            ft.Container(
                width=650,                         # mismo ancho para todas
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

    # ------------------------- BOTÓN VOLVER -------------------------

    boton_volver = ft.ElevatedButton(
        text="Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=COLOR_PRINCIPAL,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: mostrar_pantalla_menu_admin(page, repo, usuario),
    )

    # ---------------------- TARJETA CONTENEDORA ----------------------

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
                ft.Text(
                    f"Usuario autenticado: {usuario.nombre_usuario}",
                    size=14,
                    italic=True,
                    color="grey",
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

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=tarjeta,
            ),
        ],
    )

    page.add(layout)
    page.update()


# =====================================================================
#  PANTALLA TRABAJADOR: SOLO CONSULTAR PARÁMETROS (SIN EDITAR)
# =====================================================================

def mostrar_pantalla_parametros_sanidad_trabajador(page: ft.Page, repo, usuario):

    from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    page.clean()

    datos = cargar_valores()
    tarjetas = []

    # ------------------- TARJETAS SOLO LECTURA -------------------

    # Temperatura y humedad
    for categoria in ("temperatura", "humedad"):
        info = datos.get(categoria, {})

        tarjetas.append(
            ft.Container(
                width=650,                         # mismo ancho que en admin
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
                        # SIN botón de editar (solo consulta)
                    ]
                ),
            )
        )

    # Calidad del aire
    calidad = datos.get("calidad_aire", {})
    for subparam, info in calidad.items():
        tarjetas.append(
            ft.Container(
                width=650,                         # mismo ancho
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
                        # SIN botón de editar
                    ]
                ),
            )
        )

    # ------------------------- BOTÓN VOLVER -------------------------

    boton_volver = ft.ElevatedButton(
        text="Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=COLOR_PRINCIPAL,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: mostrar_pantalla_menu_trabajador(page, repo, usuario),
    )

    # ---------------------- TARJETA CONTENEDORA ----------------------

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
                ft.Text(
                    f"Usuario autenticado: {usuario.nombre_usuario}",
                    size=14,
                    italic=True,
                    color="grey",
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

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=tarjeta,
            ),
        ],
    )

    page.add(layout)
    page.update()
