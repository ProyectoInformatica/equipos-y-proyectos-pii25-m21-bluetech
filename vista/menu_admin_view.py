import flet as ft
# from vista.gestion_usuarios_view import mostrar_pantalla_gestion_usuarios
# from vista.estado_salas_view import mostrar_pantalla_estado_salas
# from vista.parametros_sanidad_view import mostrar_pantalla_parametros_sanidad

COLOR_PRINCIPAL = "blue" #color del fondo 
COLOR_TEXTO = "white" #color del texto

def mostrar_pantalla_menu_admin(page: ft.Page, repo, usuario):
    from vista.login_view import mostrar_pantalla_login
    # Limpia la página
    page.clean()

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
                bgcolor=COLOR_PRINCIPAL, #color fondo
                color=COLOR_TEXTO, #color texto
                padding=20, #distancia del contenido
                shape=ft.RoundedRectangleBorder(radius=10) #redondeo de los bordes
            ),
            expand=True, #responsibe
            on_click=on_click
        )

    # Botones con navegación
    boton_gestion_usuarios = crear_boton("Gestión de usuarios", ft.Icons.PEOPLE, #funcionalidad boton Gestión de usuarios
        #on_click=lambda e: mostrar_pantalla_gestion_usuarios(page, repo, usuario)
        )
    boton_estado_salas = crear_boton("Visualizar / cambiar estado de salas", ft.Icons.MEETING_ROOM, #funcionalidad boton Visualizar / cambiar estado de salas
        #on_click=lambda e: mostrar_pantalla_estado_salas(page, repo, usuario)
        )
    boton_parametros_sanidad = crear_boton("Consultar / cambiar parámetros de sanidad", ft.Icons.HEALTH_AND_SAFETY, #funcionalidad boton Consultar / cambiar parámetros de sanidad
        #on_click=lambda e: mostrar_pantalla_parametros_sanidad(page, repo, usuario)
        )
    boton_cerrar_sesion = crear_boton("Cerrar sesión", ft.Icons.LOGOUT, #funcionalidad boton cerrar sesión
        on_click=lambda e: mostrar_pantalla_login(page, repo))

    #contenedor de contenido principal
    tarjeta_menu = ft.Container(
        content=ft.Column([
            #título
            ft.Text(
                "🔷 Menú principal - Administrador",
                size=26, #tamaño de la letra
                weight="bold", #poner texto en negrita
                color=COLOR_PRINCIPAL
            ),
            #subtitulo
            ft.Row(
            controls=[
                    ft.Icon(ft.Icons.MANAGE_ACCOUNTS, color="grey"), #icono
                    ft.Text(f"Usuario autenticado: {usuario.nombre_usuario}", size=16, italic=True, color="grey") #texto en italica
                ],
                alignment=ft.MainAxisAlignment.CENTER #alinear texto al centro
            ),
            ft.Divider(), #linea divisora
            #botones
            boton_gestion_usuarios,
            boton_estado_salas,
            boton_parametros_sanidad,
            ft.Divider(), #linea divisora
            boton_cerrar_sesion #boton cerrar sesión
        ], 
        spacing=15,
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
                content=ft.Column(
                    controls=[tarjeta_menu], #bloque contenido principal
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ]
    )

    #añadir información nueva a la pantalla
    page.add(layout)
    page.update()