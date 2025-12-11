import flet as ft
import json

COLOR_PRINCIPAL = "blue" 
COLOR_TEXTO = "white"

def mostrar_pantalla_estado_salas(page: ft.Page, repo=None, usuario=None, origen="trabajador"):
    #importamos archivos de vista admin y trabajador para poder regresar al menu
    from vista.menu_admin_view import mostrar_pantalla_menu_admin 
    from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    #Estilo por defecto de la pagina
    page.title = "Visualización Ocupación de Salas"
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    page.clean() #limpia la pagina

    # Cargar datos del JSON
    with open("habitacion.json", "r") as archivo:
        datos = json.load(archivo)

    titulo = ft.Text("🚪 Estado de ocupación de salas", size=26, weight="bold", color=COLOR_PRINCIPAL) #título
    subtitulo = ft.Text("Introduce el ID de la habitación para consultar su estado", size=16, italic=True, color="grey") #Subtitulo

    #caja para que el usuario introduzca el Id de la habitación
    input_id = ft.TextField(label="ID habitación", width=200)
    resultado = ft.Text("", size=20)

    #verificar el estado de dicha habitación
    def verificar_estado(e):
        try:
            id_habitacion = int(input_id.value) #almacena el id introducido
            habitaciones = datos["habitaciones"]["id_habitacion"] 
            estados = datos["habitaciones"]["estado"]

            if id_habitacion in habitaciones: #comprueba que haya algun id que sea igual al introducido por el usuario
                index = habitaciones.index(id_habitacion)
                estado = estados[index] #coge el estado correspondiente al id_habitación
                resultado.value = f"El estado actual de la sala {id_habitacion} es: {estado}" #Muestra el resultado

                if estado == "libre":
                    resultado.color = "green" #texto en verde si esta libre
                elif estado == "ocupado":
                    resultado.color = "orange" #texto en naranja si esta ocupado
                else:
                    resultado.color = "black"
            else: #En caso de que el id sea erroneo, mensaje de error
                resultado.value = f"La habitación con id {id_habitacion} no existe."
                resultado.color = "red"
        except ValueError: #en caso de no ser un número, mensaje de error
            resultado.value = "Por favor, introduce un número válido."
            resultado.color = "red"
        page.update() #actualiza el estado de la pagina

    #diseño del boton para verificar el id
    boton_verificar = ft.ElevatedButton(
        "Verificar",
        icon=ft.Icons.SEARCH,
        style=ft.ButtonStyle(
            bgcolor=COLOR_PRINCIPAL,
            color=COLOR_TEXTO,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=verificar_estado #llama a la función verificar cuando pinchas el boton
    )

    #funcion para volver al menú correspondiente
    def volver_al_menu(e):
        if origen == "admin": #comprueba cual es el origen para volver al menu adecuado
            mostrar_pantalla_menu_admin(page, repo, usuario)
        else:
            mostrar_pantalla_menu_trabajador(page, repo, usuario)

    #Diseño del botón para volver al menú
    boton_volver = ft.ElevatedButton(
        "Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        style=ft.ButtonStyle(
            bgcolor="grey",
            color="white",
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=volver_al_menu #llama a la función volver al menu cuando pinchas el boton
    )

    #Diseño de la caja principal
    tarjeta_estado = ft.Container(
        content=ft.Column(
            [titulo, subtitulo, ft.Divider(), input_id, boton_verificar, resultado, boton_volver], #contenido del bloque 
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        #Diseño
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        width=600,
        height=450
    )

    #almacena toda la información que se va a mostrar por pantalla
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    controls=[tarjeta_estado],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ]
    )

    page.add(layout) #añade la información a mostrar
    page.update() #actualiza la página
