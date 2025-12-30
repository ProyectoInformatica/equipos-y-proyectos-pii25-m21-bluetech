# view/exportar_metricas_view.py
import flet as ft
from controller.exportar_metricas_controller import ExportarMetricasController

def mostrar_pantalla_exportar_metricas(page: ft.Page, repo, usuario):

    from view.menu_admin_view import mostrar_pantalla_menu_admin
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    page.clean()

    controller = ExportarMetricasController()
    mensaje = ft.Text("", size=16, weight="bold", text_align="center")

    # ---------------- EXPORTAR ----------------
    def descargar_csv(tipo):

        ok, resultado = controller.generar_csv(tipo)

        if not ok:
            mensaje.value = resultado
            mensaje.color = "red"
            page.update()
            return

        nombre_csv, csv_content = resultado

        def on_save(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    path = e.path if e.path.endswith(".csv") else e.path + ".csv"
                    with open(path, "w", encoding="utf-8-sig") as f:
                        f.write(csv_content)
                    mensaje.value = f"Archivo guardado en:\n{path}"
                    mensaje.color = "green"
                except Exception as ex:
                    mensaje.value = str(ex)
                    mensaje.color = "red"
            else:
                mensaje.value = "Descarga cancelada"
                mensaje.color = "orange"

            page.update()

        picker = ft.FilePicker(on_result=on_save)
        page.overlay.append(picker)
        page.update()

        picker.save_file(
            file_name=nombre_csv,
            allowed_extensions=["csv"]
        )

    # ---------------- BOTONES ----------------
    btn_sensores = ft.ElevatedButton(
        "Descargar Sensores (CSV)",
        icon=ft.Icons.DOWNLOAD,
        width=500,
        height=60,
        on_click=lambda e: descargar_csv("sensores"),
    )

    btn_usuarios = ft.ElevatedButton(
        "Descargar Usuarios (CSV)",
        icon=ft.Icons.DOWNLOAD,
        width=500,
        height=60,
        on_click=lambda e: descargar_csv("usuarios"),
    )

    btn_habitaciones = ft.ElevatedButton(
        "Descargar Habitaciones (CSV)",
        icon=ft.Icons.DOWNLOAD,
        width=500,
        height=60,
        on_click=lambda e: descargar_csv("habitaciones"),
    )

    def volver(e):
        if usuario.rol == "administrador":
            mostrar_pantalla_menu_admin(page, repo, usuario)
        else:
            mostrar_pantalla_menu_trabajador(page, repo, usuario)

    btn_volver = ft.ElevatedButton(
        "Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        width=500,
        height=60,
        on_click=volver
    )

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Stack(
            expand=True,
            controls=[
                ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Container(
                        width=700,
                        height=700,
                        padding=50,
                        bgcolor="white",
                        border_radius=20,
                        shadow=ft.BoxShadow(blur_radius=30, color="#30000000"),
                        content=ft.Column(
                            [
                                ft.Text("Exportar Métricas", size=34, weight="bold"),
                                ft.Divider(),
                                btn_sensores,
                                btn_usuarios,
                                btn_habitaciones,
                                mensaje,
                                ft.Divider(),
                                btn_volver,
                            ],
                            horizontal_alignment="center",
                            spacing=20,
                        ),
                    ),
                ),
            ],
        )
    )

    page.update()
