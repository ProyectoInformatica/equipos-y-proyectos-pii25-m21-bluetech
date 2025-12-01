import flet as ft
import json

RUTA_JSON = "valores_comparativos.json"

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "black"



# Cargar valores

def cargar_valores():
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# Guardar valores

def guardar_valores(data):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



#                   VISTA PRINCIPAL CON PARÁMETROS

def mostrar_pantalla_parametros_sanidad(page: ft.Page, repo, usuario):

    from vista.menu_admin_view import mostrar_pantalla_menu_admin

    page.clean()

    datos = cargar_valores()

    tarjetas = []

    
    # FUNCIÓN PARA ABRIR EL DIÁLOGO DE EDICIÓN
   
    def abrir_editor(categoria, subclave=None):
        """ subclave se usa para 'calidad_aire' """
        
        # Obtener el diccionario que se va a editar
        if subclave:
            valores = datos[categoria][subclave]
            titulo = f"Editar {subclave}"
        else:
            valores = datos[categoria]
            titulo = f"Editar {categoria}"

        # Crear campos dinámicamente
        campos = {}
        controles = []

        for k, v in valores.items():
            campo = ft.TextField(label=k, value=str(v))
            campos[k] = campo
            controles.append(campo)

        # Función guardar cambios
        def guardar_cambios(e):
            for clave, campo in campos.items():
                texto = campo.value.strip()

                # Convertir a número si es posible
                if texto.replace(".", "", 1).isdigit():
                    valor = float(texto)
                else:
                    valor = texto

                if subclave:
                    datos[categoria][subclave][clave] = valor
                else:
                    datos[categoria][clave] = valor

            guardar_valores(datos)
            dialog.open = False
            page.update()
            mostrar_pantalla_parametros_sanidad(page, repo, usuario)

        # Diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(titulo, size=20, weight="bold"),
            content=ft.Column(controles, tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo()),
                ft.FilledButton("Guardar", on_click=guardar_cambios)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def cerrar_dialogo():
            dialog.open = False
            page.update()

        page.dialog = dialog
        dialog.open = True
        page.update()


    #                   CREACIÓN DE TARJETAS DE DATOS
  

    # TEMPERATURA Y HUMEDAD
    for categoria in ("temperatura", "humedad"):
        info = datos[categoria]

        tarjetas.append(
            ft.Container(
                bgcolor="white",
                padding=15,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=8, color="grey"),
                content=ft.Column([
                    ft.Text(f"{'🌡️' if categoria=='temperatura' else '💧'} {categoria.capitalize()}",
                            size=20, weight="bold", color=COLOR_PRINCIPAL),

                    ft.Text(f"Rango: {info.get('min')} - {info.get('max')} {info.get('unidad')}"),
                    ft.Text(info.get("descripcion", ""), italic=True),

                    ft.ElevatedButton(
                        text="Editar",
                        icon=ft.Icons.EDIT,
                        bgcolor=COLOR_PRINCIPAL,
                        color="white",
                        on_click=lambda e, cat=categoria: abrir_editor(cat)
                    )
                ])
            )
        )

    # CALIDAD DEL AIRE
    calidad = datos["calidad_aire"]
    for subparam, info in calidad.items():

        tarjetas.append(
            ft.Container(
                bgcolor="white",
                padding=15,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=8, color="grey"),
                content=ft.Column([
                    ft.Text(f"🫁 {subparam}", size=20, weight="bold", color=COLOR_PRINCIPAL),
                    ft.Text(f"Máximo: {info['max']} {info['unidad']}"),
                    ft.Text(info["descripcion"], italic=True),

                    ft.ElevatedButton(
                        text="Editar",
                        icon=ft.Icons.EDIT,
                        bgcolor=COLOR_PRINCIPAL,
                        color="white",
                        on_click=lambda e, sp=subparam: abrir_editor("calidad_aire", sp)
                    )
                ])
            )
        )

    
    # BOTÓN VOLVER
 
    boton_volver = ft.ElevatedButton(
        text="Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=COLOR_PRINCIPAL,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: mostrar_pantalla_menu_admin(page, repo, usuario)
    )

    # TARJETA CONTENEDORA
    
    tarjeta = ft.Container(
        width=750,
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        content=ft.Column(
            spacing=25,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("🔬 Parámetros de Sanidad", size=28, weight="bold", color=COLOR_PRINCIPAL),
                ft.Text(f"Usuario autenticado: {usuario.nombre_usuario}", size=14, italic=True, color="grey"),

                ft.Divider(),
                ft.Column(tarjetas, spacing=20),
                ft.Divider(),
                boton_volver
            ]
        )
    )

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(expand=True, alignment=ft.alignment.center, content=tarjeta)
        ]
    )

    page.add(layout)
    page.update()
