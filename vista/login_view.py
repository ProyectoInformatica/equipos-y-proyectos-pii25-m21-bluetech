import flet as ft
from flet import Icons 
from modeloBlueTech import Rol 
from vista.menu_admin_view import mostrar_pantalla_menu_admin
from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador

def mostrar_pantalla_login(page: ft.Page, repo):
    page.controls.clear()

    # --- ELEMENTOS DEL FORMULARIO ---
    campo_usuario = ft.TextField(label="Nombre de usuario", prefix_icon=Icons.PERSON) 
    campo_contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=Icons.LOCK) 
    mensaje = ft.Text(value="", size=14) 

    def manejar_login(evento): 
        nombre_login = campo_usuario.value.strip()
        contrasena = campo_contrasena.value.strip()

        if len(nombre_login) == 0 or len(contrasena) == 0:
            mensaje.value = "Debes introducir usuario y contraseña."
            mensaje.color = "red"
            page.update()
            return

        # 1. VERIFICACIÓN DE CREDENCIALES (Doble check Admin/Trabajador)
        usuario = repo.verificar_login(nombre_login, contrasena, Rol.ADMINISTRADOR)

        if usuario is None:
            usuario = repo.verificar_login(nombre_login, contrasena, Rol.TRABAJADOR)

        if usuario is None:
            mensaje.value = "Credenciales incorrectas."
            mensaje.color = "red"
            page.update()
            return

        # --- CORRECCIÓN DEL ERROR ---
        # Usamos getattr(objeto, "nombre_atributo", valor_por_defecto)
        # Si 'estado' no existe en el JSON, asumimos que es 1 (Activo)
        estado_usuario = getattr(usuario, "estado", 1) 
        # Si 'num_registros' no existe, asumimos que es 10 (para que no pida cambiar contraseña)
        num_registros = getattr(usuario, "num_registros", 10)

        # Ahora usamos las variables seguras en el IF
        if estado_usuario == 3 or num_registros == 0 or num_registros >= 500:
            from vista.cambiar_contrasena_view import mostrar_pantalla_cambiar_contrasena
            mostrar_pantalla_cambiar_contrasena(page, repo, usuario)
            return

        # Actualizar contadores SOLO si existen en el objeto
        if hasattr(usuario, "num_registros"):
            usuario.num_registros += 1
        
        if hasattr(usuario, "estado"):
            usuario.estado = 1
            
        # Solo guardamos cambios si el repositorio lo soporta
        try:
            repo.guardar_cambios()
        except Exception:
            pass # Ignoramos errores de guardado si el JSON es estático

        # --- FIN DE LA CORRECCIÓN ---

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

    boton_login = ft.ElevatedButton(
        text="Iniciar sesión",
        on_click=manejar_login,
        bgcolor="blue",
        color="white"
    )

    # --- PANEL DE SENSORES ---
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
        bgcolor="#AA002040", 
        border=ft.border.all(1, "white24"), 
        border_radius=15,
        width=350,
    )

    # --- LAYOUT PRINCIPAL ---
    layout = ft.Stack(
        controls=[
            ft.Image(src="img/fondo_login.png", fit=ft.ImageFit.COVER, expand=True),
            
            ft.Container(content=panel_info_sensores, left=50, top=380),

            ft.Container(
                left=600, top=0, right=0, bottom=0, expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src="img/avatar_usuario.png", width=150, height=150),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Inicio de sesión", size=20, weight="bold", color="blue"),
                                    campo_usuario,
                                    campo_contrasena,
                                    boton_login,
                                    mensaje
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=10,
                            padding=20,
                            shadow=ft.BoxShadow(blur_radius=15, color="grey"),
                            width=450
                        )
                    ]
                )
            )
        ]
    )

    page.add(layout)