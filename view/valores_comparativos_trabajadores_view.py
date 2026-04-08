import flet as ft
from controller.valores_comparativos_controller import obtener_valores

COLOR_PRIMARIO = ft.Colors.BLUE_800
COLOR_FONDO_INFO = ft.Colors.BLUE_GREY_50

def mostrar_pantalla_parametros_sanidad_trabajador(page: ft.Page, repo, usuario):
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    page.clean()
    
    #Obtención de datos desde el controlador
    datos = obtener_valores()
    tarjetas = []

    #--- GENERADOR DE TARJETAS INFORMATIVAS ---
    def crear_tarjeta_info(titulo, valor, unidad, descripcion, icono, color_icono):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icono, color=color_icono, size=24),
                    ft.Text(titulo, size=18, weight="bold", color=ft.Colors.BLACK87),
                ], alignment="start"),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    ft.Text("Rango Seguro: ", weight="bold", size=14),
                    ft.Text(f"{valor} {unidad}", size=14, color=COLOR_PRIMARIO),
                ]),
                ft.Text(descripcion, italic=True, size=12, color=ft.Colors.BLUE_GREY_400),
            ], spacing=5),
            bgcolor="white",
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, "black"))
        )

    #Procesar Temperatura y Humedad
    for cat in ["temperatura", "humedad"]:
        info = datos.get(cat, {})
        rango = f"{info.get('min')} a {info.get('max')}"
        
        icono = ft.Icons.THERMOSTAT if cat == "temperatura" else ft.Icons.WATER_DROP
        color = ft.Colors.ORANGE_800 if cat == "temperatura" else ft.Colors.BLUE_600
        
        tarjetas.append(crear_tarjeta_info(
            cat.capitalize(), rango, info.get('unidad', ''), 
            info.get('descripcion', ''), icono, color
        ))

    #Procesar Calidad del Aire
    calidad = datos.get("calidad_aire", {})
    for sub, info in calidad.items():
        tarjetas.append(crear_tarjeta_info(
            sub, f"Máx {info.get('max')}", info.get('unidad', ''), 
            info.get('descripcion', ''), ft.Icons.AIR_ROUNDED, ft.Colors.TEAL_600
        ))

    #--- ESTRUCTURA DE LA PÁGINA ---
    contenido_principal = ft.Container(
        width=600,
        height=700,
        bgcolor="white",
        border_radius=20,
        padding=40,
        shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.BLACK26),
        content=ft.Column([
            #Cabecera
            ft.Row([
                ft.Icon(ft.Icons.HEALTH_AND_SAFETY_OUTLINED, color=COLOR_PRIMARIO, size=35),
                ft.Column([
                    ft.Text("Estándares de Sanidad", size=24, weight="bold", color=COLOR_PRIMARIO),
                    ft.Text("Valores de referencia para el centro", size=14, color="grey"),
                ], spacing=0)
            ], alignment="center"), 
            ft.Divider(height=30),
            ft.Container(
                expand=True,
                content=ft.Column(tarjetas, scroll="auto", spacing=15) 
            ),
            ft.Divider(height=30),
            #Botón Volver
            ft.ElevatedButton(
                "Regresar al Menú",
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                on_click=lambda _: mostrar_pantalla_menu_trabajador(page, repo, usuario),
                color="white",
                bgcolor=COLOR_PRIMARIO,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        ], horizontal_alignment="center")
    )

    page.add(
        ft.Stack([
            #Fondo con ajuste de imagen seguro
            ft.Image(src="img/fondo.png", fit="cover", expand=True),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.4, "black"),
                alignment=ft.Alignment(0, 0), 
                content=contenido_principal
            )
        ], expand=True)
    )
    
    page.update()