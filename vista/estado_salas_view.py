import flet as ft
import json

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "white"

def mostrar_pantalla_estado_salas(page: ft.Page, repo=None, usuario=None, origen="trabajador"):
    from vista.menu_admin_view import mostrar_pantalla_menu_admin
    from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    page.title = "Estado de salas"
    page.window_width = 1000
    page.window_height = 600
    page.window_resizable = True
    page.clean()

    def cargar_datos():
        with open("habitacion.json", "r") as archivo:
            return json.load(archivo)

    datos = cargar_datos()

    titulo = ft.Text("🏨 Estado y gestión de salas", size=26, weight="bold", color=COLOR_PRINCIPAL)
    resultado = ft.Text("", size=18)
    input_id = ft.TextField(label="ID habitación", width=200)

    boton_cambiar = ft.ElevatedButton("Cambiar estado", disabled=True)

    lista_salas = ft.ListView(expand=True, spacing=10, padding=10)

    def refrescar_lista():
        lista_salas.controls.clear()
        for i, id_hab in enumerate(datos["habitaciones"]["id_habitacion"]):
            estado = datos["habitaciones"]["estado"][i]
            color = "green" if estado == "libre" else "orange"

            lista_salas.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"Sala {id_hab}", weight="bold"),
                            ft.Text(estado, color=color)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor="#f5f5f5",
                    on_click=lambda e, id=id_hab: seleccionar_sala(id)
                )
            )
        page.update()

    def seleccionar_sala(id_habitacion):
        input_id.value = str(id_habitacion)
        verificar_estado(None)

    def verificar_estado(e):
        try:
            id_habitacion = int(input_id.value)
            habitaciones = datos["habitaciones"]["id_habitacion"]

            if id_habitacion in habitaciones:
                index = habitaciones.index(id_habitacion)
                estado = datos["habitaciones"]["estado"][index]

                resultado.value = f"Estado actual de la sala {id_habitacion}: {estado}"
                resultado.color = "green" if estado == "libre" else "orange"

                boton_cambiar.disabled = False
                boton_cambiar.data = index
            else:
                resultado.value = "La habitación no existe."
                resultado.color = "red"
                boton_cambiar.disabled = True
        except ValueError:
            resultado.value = "Introduce un ID válido."
            resultado.color = "red"
            boton_cambiar.disabled = True

        page.update()

    def cambiar_estado(e):
        index = boton_cambiar.data
        estado_actual = datos["habitaciones"]["estado"][index]
        nuevo_estado = "libre" if estado_actual == "ocupado" else "ocupado"

        datos["habitaciones"]["estado"][index] = nuevo_estado

        with open("habitacion.json", "w") as archivo:
            json.dump(datos, archivo, indent=4)

        resultado.value = f"Estado actualizado: {nuevo_estado}"
        resultado.color = "green" if nuevo_estado == "libre" else "orange"
        refrescar_lista()

    boton_cambiar.on_click = cambiar_estado

    boton_verificar = ft.ElevatedButton("Verificar", icon=ft.Icons.SEARCH, on_click=verificar_estado)

    def volver_al_menu(e):
        if origen == "admin":
            mostrar_pantalla_menu_admin(page, repo, usuario)
        else:
            mostrar_pantalla_menu_trabajador(page, repo, usuario)

    boton_volver = ft.ElevatedButton(
        "Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        on_click=volver_al_menu,
        bgcolor="grey",
        color="white"
    )

    panel_izquierdo = ft.Container(
        width=300,
        bgcolor="white",
        border_radius=15,
        padding=15,
        content=ft.Column(
            [
                ft.Text("📋 Salas disponibles", weight="bold", size=18),
                ft.Divider(),
                lista_salas
            ]
        )
    )

    # 🔥 AQUÍ ESTÁ EL ARREGLO REAL
    panel_derecho = ft.Container(
        bgcolor="white",
        border_radius=15,
        padding=30,
        width=600,
        content=ft.Column(
            [
                titulo,
                ft.Divider(),
                input_id,
                boton_verificar,
                resultado,
                boton_cambiar,
                ft.Divider(),
                boton_volver
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Row(
                    [panel_izquierdo, panel_derecho],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        ]
    )

    page.add(layout)
    refrescar_lista()
