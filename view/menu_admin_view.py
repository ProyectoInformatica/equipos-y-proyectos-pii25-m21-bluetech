import flet as ft
from view.gestion_usuarios_view import mostrar_pantalla_gestion_usuarios
from view.estado_salas_view import mostrar_pantalla_estado_salas
from view.mapa_habitaciones_admin_view import mostrar_pantalla_mapa_admin
from view.valores_comparativos_admin_view import mostrar_pantalla_parametros_sanidad
from view.exportar_metricas_view import mostrar_pantalla_exportar_metricas
from view.consumo_sensores_view import mostrar_pantalla_consumo_sensores

COLOR_PRINCIPAL = "blue" #color del fondo 
COLOR_TEXTO = "white" #color del texto

def mostrar_pantalla_menu_admin(page: ft.Page, repo, usuario):
    from view.login_view import mostrar_pantalla_login
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
                bgcolor=COLOR_PRINCIPAL, #color fondo
                color=COLOR_TEXTO, #color texto
                padding=20, #distancia del contenido
                shape=ft.RoundedRectangleBorder(radius=10) #redondeo de los bordes
            ),
            expand=True, #responsibe
            on_click=on_click
        )
    
    # callback para volver desde la pantalla de gestión
    def volver_desde_gestion():
        mostrar_pantalla_menu_admin(page, repo, usuario)

    def ir_a_mapa_habitaciones(e):
        mostrar_pantalla_mapa_admin(
            page=page,
            repo=repo,
            usuario=usuario
        )

    def ir_a_gestion_usuarios(e):
        mostrar_pantalla_gestion_usuarios(
            page=page,
            usuario=usuario,
            repo=repo,
            on_volver=volver_desde_gestion
        )
    
    def ir_a_visulizar_cambiar_estado(e):
        mostrar_pantalla_estado_salas(
            page=page,
            repo=repo,
            usuario=usuario,
            origen="admin"
        )

    def ir_a_parametros_sanidad(e):
        mostrar_pantalla_parametros_sanidad(
            page=page,
            repo=repo,
            usuario=usuario
        )

    def ir_a_consumo_energetico(e):
        mostrar_pantalla_consumo_sensores(
            page=page,
            usuario=usuario,
            on_volver = volver_desde_gestion,
        )

    def ir_a_exportar_metricas(e):
        mostrar_pantalla_exportar_metricas(
            page=page,
            repo=repo,
            usuario=usuario
        )

    def cerrar_sesion(e):
        usuario.estado = 2
        repo.guardar_cambios()
        mostrar_pantalla_login(page, repo)

    # Botones con navegación
    boton_mapa = crear_boton("Mapa de habitaciones", ft.Icons.MAP,  #funcionalidad boton mapa
        on_click=ir_a_mapa_habitaciones,
    )
    boton_gestion_usuarios = crear_boton("Gestión de usuarios", ft.Icons.PEOPLE, #funcionalidad boton Gestión de usuarios
        on_click=ir_a_gestion_usuarios,
    )
    boton_estado_salas = crear_boton("Visualizar / cambiar estado de salas", ft.Icons.MEETING_ROOM, #funcionalidad boton Visualizar estado de salas
        on_click=ir_a_visulizar_cambiar_estado,
    )
    boton_parametros_sanidad = crear_boton("Consultar / cambiar parámetros de sanidad", ft.Icons.HEALTH_AND_SAFETY, #funcionalidad boton Consultar / cambiar parámetros de sanidad
        on_click=ir_a_parametros_sanidad,
    )
    boton_consumo_energetico = crear_boton("Consumo energético", ft.Icons.BOLT, #funcionalidad boton Gestión de usuarios
        on_click=ir_a_consumo_energetico,
    )
    boton_exportar_metricas = crear_boton("Exportar metricas", ft.Icons.DOWNLOAD, #funcionalidad boton cerrar sesión
        on_click=ir_a_exportar_metricas,
    )
    boton_cerrar_sesion = crear_boton("Cerrar sesión", ft.Icons.LOGOUT, #funcionalidad boton cerrar sesión
        on_click=lambda e: cerrar_sesion(e),
    )

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
            boton_mapa,
            boton_gestion_usuarios,
            boton_estado_salas,
            boton_parametros_sanidad,
            boton_consumo_energetico,
            boton_exportar_metricas,
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
        height=620
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