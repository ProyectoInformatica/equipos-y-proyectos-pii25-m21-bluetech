# vista/exportar_metricas_view.py
import json
import pandas as pd
import os
import flet as ft

def mostrar_pantalla_exportar_metricas(page: ft.Page, usuario, on_volver):
    page.controls.clear()

    mensaje = ft.Text("", size=16, weight="bold", color="green", text_align="center")

    def combinar_sensores():
        try:
            # Cargar los 3 archivos
            with open("sensores_temperatura.json", "r", encoding="utf-8") as f:
                temp = json.load(f)["sensores_temp"]
            with open("sensores_humedad.json", "r", encoding="utf-8") as f:
                hum = json.load(f)["sensores_hum"]
            with open("sensores_calidad_aire.json", "r", encoding="utf-8") as f:
                aire = json.load(f)["sensores_cali_aire"]

            # Crear DataFrame base con id_sensor
            df = pd.DataFrame({
                "id_sensor": temp["id_sensor"],
                "temperatura": temp["temperatura"],
                "humedad": hum["humedad"]
            })

            # Añadir calidad del aire (anidado)
            cal_aire = aire["calidad_aire"]
            for key in cal_aire:
                df[key] = cal_aire[key]

            return df

        except Exception as ex:
            mensaje.value = f"Error al leer sensores: {ex}"
            mensaje.color = "red"
            page.update()
            return None

    def descargar_csv(e, tipo):
        try:
            if tipo == "sensores":
                df = combinar_sensores()
                if df is None or df.empty:
                    mensaje.value = "No se pudieron cargar los datos de sensores"
                    mensaje.color = "red"
                    page.update()
                    return
                nombre_csv = "sensores_completos.csv"

            elif tipo == "usuarios":
                with open("usuarios.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                df = pd.DataFrame(data.get("usuarios", []))
                nombre_csv = "usuarios.csv"

            elif tipo == "habitaciones":
                with open("habitacion.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                hab = data.get("habitaciones", {})
                df = pd.DataFrame({
                    "id_habitacion": hab.get("id_habitacion", []),
                    "estado": hab.get("estado", [])
                })
                nombre_csv = "habitaciones.csv"

            if df.empty:
                mensaje.value = "No hay datos para exportar"
                mensaje.color = "orange"
                page.update()
                return

            csv_content = df.to_csv(index=False, encoding="utf-8-sig")

            def on_save(result: ft.FilePickerResultEvent):
                if result.path:
                    try:
                        save_path = result.path if result.path.lower().endswith(".csv") else result.path + ".csv"
                        with open(save_path, "w", encoding="utf-8-sig", newline='') as f:
                            f.write(csv_content)
                        mensaje.value = f"¡Descarga completada!\nGuardado en: {save_path}"
                        mensaje.color = "green"
                    except Exception as ex:
                        mensaje.value = f"Error al guardar: {ex}"
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
                dialog_title="Guardar como CSV (Excel)",
                allowed_extensions=["csv"]
            )

        except Exception as ex:
            mensaje.value = f"Error: {ex}"
            mensaje.color = "red"
            page.update()

    # === BOTONES ===
    btn_sensores = ft.ElevatedButton(
        "Descargar Todos los Sensores (CSV)",
        icon=ft.Icons.DOWNLOAD,
        bgcolor="#1565c0",
        color="white",
        width=500,
        height=60,
        on_click=lambda e: descargar_csv(e, "sensores")
    )

    btn_usuarios = ft.ElevatedButton(
        "Descargar Usuarios (CSV)",
        icon=ft.Icons.DOWNLOAD,
        bgcolor="#1565c0",
        color="white",
        width=500,
        height=60,
        on_click=lambda e: descargar_csv(e, "usuarios")
    )

    btn_habitaciones = ft.ElevatedButton(
        "Descargar Habitaciones (CSV)",
        icon=ft.Icons.DOWNLOAD,
        bgcolor="#1565c0",
        color="white",
        width=500,
        height=60,
        on_click=lambda e: descargar_csv(e, "habitaciones")
    )

    btn_volver = ft.ElevatedButton(
        "Volver al menú",
        icon=ft.Icons.ARROW_BACK,
        bgcolor="#1565c0",
        color="white",
        width=500,
        height=60,
        on_click=lambda e: on_volver()
    )

    # === LAYOUT ===
    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Container(
                    width=1000,
                    padding=50,
                    bgcolor="white",
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=30, color="#30000000"),
                    content=ft.Column([
                        ft.Text("Exportar Métricas", size=34, weight="bold", color="#1565c0", text_align="center"),
                        ft.Text(f"Usuario: {usuario.nombre_usuario}", color="#555", size=16, italic=True),
                        ft.Divider(height=1, color="#e0e0e0"),

                        ft.Text("Selecciona el archivo que deseas exportar a Excel (CSV):", size=20, text_align="center", color="#333"),
                        ft.Container(height=50),

                        btn_sensores,
                        ft.Container(height=25),
                        btn_usuarios,
                        ft.Container(height=25),
                        btn_habitaciones,

                        ft.Container(height=50),
                        mensaje,

                        ft.Container(height=40),
                        btn_volver
                    ],
                    horizontal_alignment="center",
                    spacing=18,
                    scroll=ft.ScrollMode.AUTO)
                )
            )
        ], expand=True)
    )