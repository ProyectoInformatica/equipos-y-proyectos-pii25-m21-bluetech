import flet as ft
from modeloBlueTech import Rol
from flet import Icons 
from vista.menu_admin_view import mostrar_pantalla_menu_admin
from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador

def mostrar_pantalla_login(page: ft.Page, repo):
    page.controls.clear()

    # --- ELEMENTOS DEL FORMULARIO ---
    campo_usuario = ft.TextField(label="Nombre de usuario", prefix_icon=Icons.PERSON)
    campo_contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=Icons.LOCK)
    campo_rol = ft.Dropdown(
        label="Rol",
        options=[
            ft.dropdown.Option("Administrador"),
            ft.dropdown.Option("Trabajador")
        ]
    )
    mensaje = ft.Text(value="", size=14)

    def manejar_login(evento):
        nombre_login = campo_usuario.value.strip()
        contrasena = campo_contrasena.value.strip()
        rol_texto = campo_rol.value

        if len(nombre_login) == 0 or len(contrasena) == 0 or rol_texto is None:
            mensaje.value = "Debes introducir usuario, contraseña y seleccionar un rol."
            mensaje.color = "red"
            page.update()
            return
        
        rol_seleccionado = None
        if rol_texto == "Administrador":
            rol_seleccionado = Rol.ADMINISTRADOR
        elif rol_texto == "Trabajador":
            rol_seleccionado = Rol.TRABAJADOR

        usuario = repo.verificar_login(nombre_login, contrasena, rol_seleccionado)

        if usuario is None:
            mensaje.value = "Credenciales incorrectas. Inténtalo de nuevo."
            mensaje.color = "red"
        else:
            mensaje.value = "Inicio de sesión correcto."
            mensaje.color = "green"
            page.update()
            if usuario.es_administrador():
                mostrar_pantalla_menu_admin(page, repo, usuario)
                return
            if usuario.es_trabajador():
                mostrar_pantalla_menu_trabajador(page, repo, usuario)
                return

        page.update()

    boton_login = ft.ElevatedButton(text="Iniciar sesión", on_click=manejar_login)

    # --- NUEVO: PANEL DE SENSORES (SIMPLIFICADO) ---
    panel_info_sensores = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("MONITOR DE SISTEMA (Consumo)", weight="bold", color="white", size=16),
                ft.Divider(color="white54", thickness=1),
                
                ft.Text("• ESP32 + CAM (OV2640): ~2.0 W (Peak)", color="white70", size=12),
                ft.Text("• DHT11/22 + LDR + Anemómetro: ~0.1 W", color="white70", size=12),
                ft.Text("• MQ-2 (Humo) + MQ-135 (Aire): ~1.6 W", color="white70", size=12),
                ft.Text("• HC-SR04 + Caudalímetro G1/2: ~0.2 W", color="white70", size=12),
                ft.Text("• Ventilador 5V + LEDs: ~1.5 W", color="white70", size=12),
                ft.Text("• Motor DC 12V: ~12.0 - 24.0 W", weight="bold", color="orange", size=12),
                
                ft.Divider(color="white54", thickness=1),
                ft.Text("Consumo Total Est.: ~20 W", weight="bold", color="cyan", size=14),
            ],
            spacing=5,
        ),
        padding=20,
        # Usamos Strings hexadecimales para evitar el error de 'colors'
        # He aumentado la opacidad (AA en vez de 99) porque ya no tenemos el blur
        bgcolor="#AA002040", 
        border=ft.border.all(1, "white24"), 
        border_radius=15,
        width=350,
        # ELIMINADO: backdrop_filter (esto causaba el segundo error)
    )

    # --- LAYOUT PRINCIPAL ---
    layout = ft.Stack(
        controls=[
            # 1. Imagen de fondo
            ft.Image(
                src="img/fondo_login.png", 
                fit=ft.ImageFit.COVER,
                expand=True
            ),
            
            # 2. PANEL DE INFORMACIÓN
            ft.Container(
                content=panel_info_sensores,
                left=50,   
                top=380,   
            ),

            # 3. FORMULARIO DE LOGIN
            ft.Container(
                left=600, 
                top=0,
                right=0,
                bottom=0,
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src="img/avatar_usuario.png", width=150, height=150),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Inicio de sesión", size=20, weight="bold"),
                                    campo_usuario, 
                                    campo_contrasena,
                                    campo_rol,
                                    boton_login,
                                    mensaje
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=10,
                            padding=20,
                            # Corrección: si boxshadow da error, se puede quitar, pero suele ser compatible.
                            shadow=ft.BoxShadow(blur_radius=15, color="grey"),
                            width=450
                        )
                    ]
                )
            )
        ]
    )

    page.add(layout)