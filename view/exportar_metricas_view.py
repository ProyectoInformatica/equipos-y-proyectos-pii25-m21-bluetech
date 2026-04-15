import flet as ft
from controller.exportar_metricas_controller import ExportarMetricasController

#Silenciar warning de panda (Recomienda otra version)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def mostrar_pantalla_exportar_metricas(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()
    controller = ExportarMetricasController()
    tablas = controller.obtener_tablas()

    checkboxes = []
    seleccionadas = []
    formato_seleccionado = "excel"

    def toggle_tabla(e):
        if e.control.value:
            seleccionadas.append(e.control.label)
        else:
            seleccionadas.remove(e.control.label)

    # Crear checkboxes dinámicos
    for t in tablas:
        cb = ft.Checkbox(label=t, value=False, on_change=toggle_tabla)
        checkboxes.append(cb)

    def seleccionar_formato(tipo):
        nonlocal formato_seleccionado
        formato_seleccionado = tipo
        btn_excel.bgcolor = "blue" if tipo == "excel" else None
        btn_csv.bgcolor = "blue" if tipo == "csv" else None
        page.update()

    btn_excel = ft.Container(
        content=ft.Image(src="img/excel.png", width=60, height=60),
        on_click=lambda e: seleccionar_formato("excel"),
        padding=10,
        border_radius=10,
        bgcolor="blue" 
    )

    btn_csv = ft.Container(
        content=ft.Image(src="img/csv.png", width=60, height=60),
        on_click=lambda e: seleccionar_formato("csv"),
        padding=10,
        border_radius=10,
    )

    formato = ft.RadioGroup(
        content=ft.Row(
            [btn_excel, btn_csv],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        value="excel"
    )

    mensaje = ft.Text()

    def exportar_click(e):
        ok, res = controller.exportar(seleccionadas, formato_seleccionado)
        if ok:
            if isinstance(res, list):
                mensaje.value = "✅ CSVs generados en Desktop/BlueTechMetricas"
            else:
                mensaje.value = f"✅ Excel generado:\n{res}"
            mensaje.color = "green"
        else:
            mensaje.value = f"❌ {res}"
            mensaje.color = "red"
        page.update()

    UI = ft.Container(
        content=ft.Column(
            [
                ft.Text("2. Seleccionar Tablas", size=20, weight="bold"),
                ft.Column(checkboxes, scroll="auto", height=300),
                ft.Divider(),
                ft.Text("3. Formato de Exportación", size=20, weight="bold"),
                formato,
                ft.ElevatedButton(
                    "Generar y Exportar",
                    on_click=exportar_click,
                    width=300
                ),
                mensaje,
                ft.TextButton(
                    "← Volver al menú",
                    on_click=lambda _: mostrar_pantalla_menu_admin(page, repo, usuario)
                ),
            ],
            horizontal_alignment="center"
        ),
        padding=30,
        bgcolor="white",
        border_radius=15,
        width=400,
        height=700
    )

    page.add(
        ft.Container(
            content=UI,
            alignment=ft.Alignment(0, 0),
            expand=True
        )
    )

    page.update()