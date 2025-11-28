import flet as ft
from vista.estado_salas_view import mostrar_pantalla_estado_salas
from vista.cambiar_estado_view import mostrar_pantalla_cambiar_estado
from vista.mapa_habitaciones_trabajadores_view import mostrar_pantalla_mapa_habitaciones_trabajadores
# from vista.parametros_sanidad_view import mostrar_pantalla_parametros_sanidad

COLOR_PRINCIPAL = "blue" #color del fondo
COLOR_TEXTO = "white" #color del texto

def mostrar_pantalla_menu_trabajador(page: ft.Page, repo, usuario):
    from vista.login_view import mostrar_pantalla_login
    # Limpia la página
    page.clean()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None
    page.bgcolor = None
    
    #funcion para diseño de los botones
    def crear_boton(texto, icono, on_click=None):
        return ft.ElevatedButton(
            #desglose de los botones en filas
            content=ft.Row([
                ft.Icon(icono, size=20), #icono
                ft.Text(texto) #texto
            ], 
            alignment=ft.MainAxisAlignment.START), #alinea el contenido del boton a la izquierda
            #diseño
            style=ft.ButtonStyle(
                bgcolor=COLOR_PRINCIPAL,
                color=COLOR_TEXTO,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            expand=True, #responsibe
            on_click=on_click
        )

    # Botones con navegación
    boton_estado_salas = crear_boton("Visualizar estado de salas", ft.Icons.MEETING_ROOM, #funcionalidad boton Visualizar estado de salas
        on_click=lambda e: mostrar_pantalla_estado_salas(page, repo, usuario, origen="trabajador")
    )
    boton_cambiar_estado = crear_boton("Cambiar estado de salas", ft.Icons.SWAP_HORIZ,  #funcionalidad boton Actualizar estado de salas
        on_click=lambda e: mostrar_pantalla_cambiar_estado(page, repo, usuario, origen="trabajador")
    )
    boton_mapa_habitaciones = crear_boton("Mapa estados habitaciones", ft.Icons.MAP,  #funcionalidad boton Mostrar mapa de las salas
        on_click=lambda e: mostrar_pantalla_mapa_habitaciones_trabajadores(page, repo, usuario)
    )
    boton_parametros_sanidad = crear_boton("Consultar parámetros de sanidad", ft.Icons.HEALTH_AND_SAFETY, #funcionalidad boton Consultar parámetros de sanidad
        # on_click=lambda e: mostrar_pantalla_parametros_sanidad(page, repo, usuario)
    )
    boton_cerrar_sesion = crear_boton("Cerrar sesión", ft.Icons.LOGOUT, #funcionalidad boton cerrar sesión
        on_click=lambda e: mostrar_pantalla_login(page, repo)
    )

    #contenedor de contenido principal
    tarjeta_menu = ft.Container(
        content=ft.Column([
            #título
            ft.Text(
                "🔷 Menú principal - Trabajador",
                size=26,
                weight="bold", #poner texto en negrita
                color=COLOR_PRINCIPAL
            ),
            #subtitulo
            ft.Row(
                controls=[ 
                    ft.Icon(ft.Icons.BADGE, color="grey"), #icono
                    ft.Text(f"Usuario autenticado: {usuario.nombre_usuario}", size=16, italic=True, color="grey") #texto en italica
                ],
                alignment=ft.MainAxisAlignment.CENTER #alinear texto al centro
            ),
            ft.Divider(), #linea divisora
            #botones
            boton_estado_salas,
            boton_cambiar_estado,
            boton_mapa_habitaciones,
            boton_parametros_sanidad,
            ft.Divider(), #linea divisora
            boton_cerrar_sesion #boton cerrar sesión
        ], spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        width=600,
        height=500
    )

    #toda la información que se va introducir en la pantalla
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True), #imagen de fondo
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,   
                content=tarjeta_menu
            )
        ]
    )

    #añadir información nueva a la pantalla
    page.add(layout)
    page.update()