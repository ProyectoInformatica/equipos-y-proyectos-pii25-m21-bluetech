import flet as ft
from controller.valores_comparativos_controller import obtener_valores, actualizar_valores

COLOR_PRIMARIO = ft.Colors.BLUE_700
COLOR_FONDO_TARJETA = ft.Colors.WHITE
COLOR_TEXTO_SECUNDARIO = ft.Colors.BLUE_GREY_400

def mostrar_pantalla_parametros_sanidad(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()
    
    #Carga de datos inicial
    datos = obtener_valores()
    
    #--- FUNCIONES DE APOYO ---
    def mostrar_mensaje(texto, es_error=True):
        snack = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=ft.Colors.RED_400 if es_error else ft.Colors.GREEN_400
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def abrir_editor(categoria, subclave=None):
        valores_actuales = datos[categoria][subclave] if subclave else datos[categoria]
        titulo = f"Configurar {subclave if subclave else categoria.capitalize()}"
        campos_controles = {}
        
        #Definir qué campos se pueden editar según la categoría
        campos_a_editar = ["max", "unidad", "descripcion"] if categoria == "calidad_aire" else ["min", "max", "unidad", "descripcion"]

        for clave in campos_a_editar:
            valor_original = valores_actuales.get(clave, "")
            input_field = ft.TextField(
                label=clave.upper(),
                value=str(valor_original),
                border_radius=10,
                focused_border_color=COLOR_PRIMARIO
            )
            campos_controles[clave] = input_field

        def guardar_cambios(e):
            try:
                #Validar y convertir números
                for c in ["min", "max"]:
                    if c in campos_controles:
                        val_str = campos_controles[c].value.replace(",", ".")
                        float(val_str)

                #Aplicar cambios al diccionario local
                for clave, control in campos_controles.items():
                    nuevo_valor = control.value.strip()
                    if clave in ["min", "max"]:
                        nuevo_valor = float(nuevo_valor.replace(",", "."))
                    
                    if subclave:
                        datos[categoria][subclave][clave] = nuevo_valor
                    else:
                        datos[categoria][clave] = nuevo_valor
                
                #Persistencia
                actualizar_valores(datos)
                
                #Cerrar modal
                modal.open = False
                page.update()
                
                mostrar_mensaje("Parámetros actualizados con éxito", es_error=False)
                mostrar_pantalla_parametros_sanidad(page, repo, usuario)
                
            except ValueError:
                mostrar_mensaje("Error: Los valores Min/Max deben ser numéricos.")
            except Exception as ex:
                mostrar_mensaje(f"Error inesperado: {ex}")

        #Definición del Modal
        modal = ft.AlertDialog(
            title=ft.Text(titulo, weight=ft.FontWeight.BOLD),
            content=ft.Column([campos_controles[c] for c in campos_a_editar], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: (setattr(modal, "open", False), page.update())),
                ft.ElevatedButton("Guardar", bgcolor=COLOR_PRIMARIO, color=ft.Colors.WHITE, on_click=guardar_cambios),
            ],
        )
        
        #Abrir modal 
        page.overlay.append(modal)
        modal.open = True
        page.update()

    #--- CONSTRUCCIÓN DE TARJETAS ---
    lista_tarjetas = []

    #Temperatura y Humedad
    for cat in ["temperatura", "humedad"]:
        info = datos[cat]
        icono = "🌡️" if cat == "temperatura" else "💧"
        lista_tarjetas.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"{icono} {cat.capitalize()}", size=18, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_ROUNDED, 
                            icon_color=COLOR_PRIMARIO, 
                            on_click=lambda e, c=cat: abrir_editor(c)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Rango óptimo: {info['min']} - {info['max']} {info['unidad']}", size=16),
                    ft.Text(info['descripcion'], italic=True, color=COLOR_TEXTO_SECUNDARIO, size=13),
                ]),
                bgcolor=COLOR_FONDO_TARJETA, padding=20, border_radius=15, 
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black"))
            )
        )

    #Calidad del Aire
    calidad = datos["calidad_aire"]
    for sub, info in calidad.items():
        lista_tarjetas.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"🌬️ {sub}", size=18, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_ROUNDED, 
                            icon_color=COLOR_PRIMARIO, 
                            on_click=lambda e, s=sub: abrir_editor("calidad_aire", s)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Límite máximo: {info['max']} {info['unidad']}", size=16),
                    ft.Text(info['descripcion'], italic=True, color=COLOR_TEXTO_SECUNDARIO, size=13),
                ]),
                bgcolor=COLOR_FONDO_TARJETA, padding=20, border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black"))
            )
        )

    #--- DISEÑO FINAL ---
    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit="cover", expand=True, opacity=0.5), 
            ft.Container(
                alignment=ft.Alignment(0, 0), 
                content=ft.Container(
                    width=700, 
                    height=700, 
                    bgcolor=ft.Colors.WHITE, 
                    border_radius=20, 
                    padding=30,
                    content=ft.Column([
                        ft.Text("Configuración de Sanidad", size=28, weight="bold", color=COLOR_PRIMARIO),
                        ft.Text("Define los umbrales críticos para los sensores", color=ft.Colors.GREY_600),
                        ft.Divider(height=20),
                        ft.Column(lista_tarjetas, scroll="auto", expand=True, spacing=15),
                        ft.Divider(height=20),
                        ft.Row([
                            ft.ElevatedButton(
                                "Volver al Menú", 
                                icon=ft.Icons.ARROW_BACK, 
                                on_click=lambda _: mostrar_pantalla_menu_admin(page, repo, usuario)
                            )
                        ], alignment="center")
                    ])
                )
            )
        ], expand=True)
    )
    page.update()