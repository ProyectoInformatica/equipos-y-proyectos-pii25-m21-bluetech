import flet as ft
from controller.habitaciones_controller import obtener_habitaciones, alternar_estado

COLOR_PRINCIPAL = ft.Colors.BLUE_800
COLOR_TEXTO = ft.Colors.WHITE

def mostrar_pantalla_estado_salas(page: ft.Page, repo=None, usuario=None, origen="trabajador"):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    
    page.title = "Estado de salas"
    page.controls.clear()
    
    datos = obtener_habitaciones()
    
    titulo = ft.Text(
        "🏨 Gestión de Salas",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=COLOR_PRINCIPAL
    )
    
    resultado = ft.Text("", size=16, weight=ft.FontWeight.W_500)
    input_id = ft.TextField(
        label="ID de la sala",
        width=250,
        border_radius=10,
        prefix_icon=ft.Icons.DOOR_FRONT_DOOR,
        on_change=lambda e: verificar_estado(e)
    )
    
    boton_cambiar = ft.ElevatedButton(
        "Alternar Estado",
        icon=ft.Icons.SWAP_HORIZ,
        disabled=True,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor={"": ft.Colors.BLUE_700, "disabled": ft.Colors.GREY_300}
        )
    )
    
    lista_salas = ft.ListView(expand=True, spacing=8, padding=5)

    #--- LÓGICA ---
    def refrescar_lista():
        lista_salas.controls.clear()
        for hab in datos:
            id_hab = hab["id_habitacion"]
            estado = hab["estado"]
            es_libre = estado.lower() == "libre"
            lista_salas.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.CIRCLE, 
                                    color=ft.Colors.GREEN if es_libre else ft.Colors.ORANGE,
                                    size=12
                                ),
                                ft.Text(f"Sala {id_hab}", weight=ft.FontWeight.W_500),
                            ], spacing=10),
                            ft.Container(
                                content=ft.Text(
                                    estado.upper(),
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREEN_900 if es_libre else ft.Colors.ORANGE_900
                                ),
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=ft.Colors.GREEN_100 if es_libre else ft.Colors.ORANGE_100,
                                border_radius=6
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=15,
                    border_radius=10,
                    bgcolor=ft.Colors.GREY_50,
                    on_click=lambda e, id=id_hab: seleccionar_sala(id),
                    on_hover=lambda e: setattr(
                        e.control, 
                        "bgcolor", 
                        ft.Colors.BLUE_50 if e.data=="true" else ft.Colors.GREY_50
                    ) or e.control.update()
                )
            )
        page.update()

    def seleccionar_sala(id_habitacion):
        input_id.value = str(id_habitacion)
        verificar_estado(None)
        page.update()

    def verificar_estado(e):
        try:
            val = input_id.value.strip()
            if not val:
                resultado.value = ""
                boton_cambiar.disabled = True
                page.update()
                return
            id_habitacion = int(val)
            habitaciones_ids = [h["id_habitacion"] for h in datos]
            if id_habitacion in habitaciones_ids:
                index = habitaciones_ids.index(id_habitacion)
                estado = datos[index]["estado"]
                resultado.value = f"La sala {id_habitacion} está actualmente: {estado.upper()}"
                resultado.color = ft.Colors.GREEN_700 if estado.lower() == "libre" else ft.Colors.ORANGE_800
                boton_cambiar.disabled = False
                boton_cambiar.data = index
            else:
                resultado.value = "ID no encontrado en el sistema."
                resultado.color = ft.Colors.RED_600
                boton_cambiar.disabled = True
        except ValueError:
            resultado.value = "Ingresa un número de ID válido."
            resultado.color = ft.Colors.RED_600
            boton_cambiar.disabled = True
        page.update()

    def ejecutar_cambio_estado(e):
        index = boton_cambiar.data
        id_hab = datos[index]["id_habitacion"]
        nuevo_estado = alternar_estado(id_hab)
        datos[index]["estado"] = nuevo_estado
        verificar_estado(None)
        refrescar_lista()
        page.snack_bar = ft.SnackBar(ft.Text(f"Sala {id_hab} ahora está {nuevo_estado}"))
        page.snack_bar.open = True
        page.update()

    def volver(e):
        page.controls.clear()
        if origen == "admin":
            mostrar_pantalla_menu_admin(page, repo, usuario)
        else:
            mostrar_pantalla_menu_trabajador(page, repo, usuario)

    boton_cambiar.on_click = ejecutar_cambio_estado

    panel_izquierdo = ft.Container(
        expand=1,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
        content=ft.Column([
            ft.Text("Lista de Salas", weight=ft.FontWeight.BOLD, size=18),
            ft.Divider(),
            lista_salas
        ])
    )

    panel_derecho = ft.Container(
        expand=2,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=40,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
        content=ft.Column([
            titulo,
            ft.Text("Selecciona una sala para gestionar su disponibilidad.", color=ft.Colors.GREY_600),
            ft.Divider(height=30),
            input_id,
            ft.Container(resultado, padding=ft.padding.only(top=10, bottom=10)),
            boton_cambiar,
            ft.Divider(height=40),
            ft.TextButton("Volver al Menú Principal", icon=ft.Icons.ARROW_BACK, on_click=volver)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit="cover", expand=True),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK), 
                padding=40,
                content=ft.Row(
                    [panel_izquierdo, panel_derecho],
                    spacing=30,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        ], expand=True)
    )

    refrescar_lista()