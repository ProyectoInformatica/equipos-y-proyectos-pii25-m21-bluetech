import flet as ft
import os
from controller.exportar_metricas_controller import ExportarMetricasController

def mostrar_pantalla_exportar_metricas(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin

    #LIMPIEZA TOTAL
    page.clean()
    page.padding = 0
    page.spacing = 0

    controller = ExportarMetricasController()

    #--- UI ---
    mensaje = ft.Text("", size=14, weight="w500", text_align="center")

    #--- FUNCIÓN PARA GUARDAR DIRECTO ---
    def descargar_csv(tipo):
        ok, res = controller.generar_csv(tipo)

        if ok:
            nombre_archivo = res[0]
            contenido = res[1]

            #Guardar en Escritorio automáticamente
            escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
            ruta = os.path.join(escritorio, nombre_archivo)

            #Asegurar extensión .csv
            if not ruta.lower().endswith(".csv"):
                ruta += ".csv"

            try:
                with open(ruta, "w", encoding="utf-8-sig") as f:
                    f.write(contenido)

                mensaje.value = f"✅ Guardado en: {ruta}"
                mensaje.color = ft.Colors.GREEN_700

            except Exception as e:
                mensaje.value = f"❌ Error al guardar: {str(e)}"
                mensaje.color = ft.Colors.RED

            page.update()

    #--- BOTONES ---
    def descargar_excel(e):
        ok, res = controller.generar_excel_completo()

        if ok:
            mensaje.value = f"✅ Excel guardado en: {res}"
            mensaje.color = ft.Colors.GREEN_700
        else:
            mensaje.value = f"❌ {res}"
            mensaje.color = ft.Colors.RED

        page.update()


    btn_excel = ft.ElevatedButton(
        "Reporte Maestro (Excel)",
        icon=ft.Icons.GRID_ON_ROUNDED,
        width=400,
        height=60,
        on_click=descargar_excel
    )

    tarjeta = ft.Container(
        content=ft.Column(
            [
                ft.Text("Exportar Métricas", size=30, weight="bold"),
                btn_excel,
                ft.OutlinedButton("Sensores (CSV)", on_click=lambda _: descargar_csv("sensores")),
                ft.OutlinedButton("Usuarios (CSV)", on_click=lambda _: descargar_csv("usuarios")),
                mensaje,
                ft.TextButton("Volver", on_click=lambda _: mostrar_pantalla_menu_admin(page, repo, usuario)),
            ],
            horizontal_alignment="center",
            spacing=15,
        ),
        bgcolor="white",
        padding=40,
        border_radius=20,
        height=450,
    )

    page.add(
        ft.Stack(
            [
                ft.Image(
                    src="img/fondo.png",
                    fit="cover",
                    expand=True,
                    width=page.width,
                    height=page.height,
                ),
                ft.Container(
                    content=tarjeta,
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                    bgcolor=ft.Colors.with_opacity(0.3, "black"),
                ),
            ],
            expand=True,
        )
    )

    page.update()