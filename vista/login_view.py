import flet as ft
from flet import Icons #Para el uso de iconos
from vista.menu_admin_view import mostrar_pantalla_menu_admin
from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador


def mostrar_pantalla_login(page: ft.Page, repo):
    # Limpia la página por si venimos de otra vista
    page.controls.clear()

    # Campos de entrada
    campo_usuario = ft.TextField(label="Nombre de usuario", prefix_icon=Icons.PERSON) #para el nombre de usuario
    campo_contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=Icons.LOCK) #para la contraseña

    mensaje = ft.Text(value="", size=14) #para posible mensaje de aviso en caso de producirse

    # Función de manejo del login
    def manejar_login(evento): #evento es para evitar errores cuando no se especifique un rol (no quitar)
        #valores introducidos
        nombre_login = campo_usuario.value.strip()
        contrasena = campo_contrasena.value.strip()

        #manejo de error (en caso de con completar alguno de los campos)
        if len(nombre_login) == 0 or len(contrasena) == 0:
            mensaje.value = "Debes introducir usuario y contraseña."
            mensaje.color = "red"
            page.update()
            return

        # Verifica credenciales (rol detectado automáticamente por el sistema)
        usuario = repo.verificar_login(nombre_login, contrasena)

        # CAMBIO 2: cortar flujo si credenciales incorrectas (evita error)
        if usuario is None:
            mensaje.value = "Credenciales incorrectas."
            mensaje.color = "red"
            page.update()
            return

        # CAMBIO 3: redirección a cambiar contraseña si aplica
        if usuario.estado == 3 or usuario.num_registros == 0 or usuario.num_registros >= 500:
            from vista.cambiar_contrasena_view import mostrar_pantalla_cambiar_contrasena
            mostrar_pantalla_cambiar_contrasena(page, repo, usuario)
            return

        # Login normal: actualiza contadores/estado y guarda
        usuario.num_registros += 1
        usuario.estado = 1
        repo.guardar_cambios()

        #mensaje en caso de acceso exitoso
        mensaje.value = "Inicio de sesión correcto."
        mensaje.color = "green"
        page.update()

        #cargado de pagina segun el rol detectado
        if usuario.es_administrador():
            mostrar_pantalla_menu_admin(page, repo, usuario) #menú de administrador
            return
        if usuario.es_trabajador():
            mostrar_pantalla_menu_trabajador(page, repo, usuario) #menú de trabajador
            return

        #actualización de la pagina
        page.update()

    # Botón de login
    boton_login = ft.ElevatedButton(
    text="Iniciar sesión",
    on_click=manejar_login,
    bgcolor="blue",
    color="white"
    )

    # Layout con fondo usando Stack
    layout = ft.Stack(
        controls=[
            # Imagen de fondo
            ft.Image(
                src="img/fondo_login.png",
                fit=ft.ImageFit.COVER,
                expand=True
            ),

            # Caja con contenido, centrado encima del fondo
            ft.Container(
                #margenes
                left=600,
                top=0,
                right=0,
                bottom=0,
                expand=True, #expand para adaptarse al tamaño de la pantalla
                alignment=ft.alignment.center, #alinear contenido dentro de la caja al centro
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,       # Centra verticalmente
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centra horizontalmente
                    controls=[
                        ft.Image(src="img/avatar_usuario.png", width=150, height=150), #imagen encima del bloque

                        #Bloque del formulario
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Inicio de sesión", size=20, weight="bold", color="blue"), #texto
                                    #campos para introducir el usuario los datos
                                    campo_usuario,
                                    campo_contrasena,
                                    boton_login, #boton de envio de datos
                                    mensaje #mensaje para informar de alertas/errores
                                ],
                                #alineación del bloque
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            bgcolor="white", #color de fondo del bloque formulario
                            border_radius=10, #borde del bloque formulario
                            padding=20, #distancia del contenido al borde del bloque formulario
                            shadow=ft.BoxShadow(blur_radius=15, color="grey"), #color y tamaño de la sombra del bloque
                            width=450 #ancho del bloque
                        )
                    ]
                )
            )
        ]
    )

    #muestra todo el contenido en la pantalla
    page.add(layout)
