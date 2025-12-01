import json
import flet as ft
from modeloBlueTech import RepositorioCredenciales


def mostrar_pantalla_gestion_usuarios(
    page: ft.Page,
    usuario,
    repo: RepositorioCredenciales,
    on_volver,
):
    """Pantalla de gestión de usuarios para el rol administrador."""

    page.controls.clear()

    # ---------- CABECERA ----------

    titulo = ft.Text(
        "Gestión de usuarios - Administrador",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="blue",
        text_align=ft.TextAlign.CENTER,
    )

    subtitulo = ft.Text(
        f"Usuario autenticado: {usuario.nombre_usuario}",
        size=14,
        italic=True,
        color="grey",
        text_align=ft.TextAlign.CENTER,
    )

    separador_superior = ft.Divider(height=1, color="#BDBDBD")  # gris clarito

    # ---------- BOTÓN LISTAR ----------

    boton_listar = ft.ElevatedButton(
        text="Listar usuarios",
        icon=ft.Icons.PEOPLE,
        bgcolor="blue",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        ),
    )

    # ---------- ELIMINAR POR ID ----------

    etiqueta_eliminar = ft.Text(
        "1) Eliminar un usuario a partir de su ID",
        size=14,
        weight=ft.FontWeight.BOLD,
    )

    campo_id = ft.TextField(
        label="ID del usuario a eliminar",
        hint_text="Introduce un ID numérico",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=260,
    )

    boton_eliminar = ft.ElevatedButton(
        text="Eliminar usuario por ID",
        icon=ft.Icons.DELETE,
        bgcolor="blue",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        ),
    )

    # ---------- LISTADO CON SCROLL ----------

    columna_listado = ft.Column(
        controls=[],
        spacing=3,
        scroll=ft.ScrollMode.AUTO,   # scroll dentro de la columna
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    contenedor_listado = ft.Container(
        content=columna_listado,
        bgcolor="#F5F5F5",           # gris muy claro
        border_radius=8,
        padding=10,
        height=260,
    )

    mensaje_estado = ft.Text("", size=12, color="green")

    boton_volver = ft.ElevatedButton(
        text="Volver al menú de administrador",
        icon=ft.Icons.ARROW_BACK,
        bgcolor="blue",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        ),
    )

    # ---------- ESTADO INTERNO PARA CONFIRMACIÓN ----------

    estado_confirmacion = {
        "esperando": False,
        "id": None,
    }

    # ---------- LÓGICA ----------

    def cargar_listado():
        """Rellena la columna con los usuarios del repositorio."""
        if not hasattr(repo, "usuarios") or repo.usuarios is None:
            repo.cargar_datos()

        columna_listado.controls.clear()

        if not repo.usuarios:
            columna_listado.controls.append(
                ft.Text("No hay usuarios registrados.", size=12)
            )
        else:
            for u in repo.usuarios:
                rol_str = str(u.rol)
                texto = (
                    f"ID: {u.id_usuario} | "
                    f"Usuario (login): {u.nombre_usuario} | "
                    f"Rol: {rol_str}"
                )
                columna_listado.controls.append(ft.Text(texto, size=12))

        mensaje_estado.value = "Listado de usuarios actualizado."
        mensaje_estado.color = "green"
        page.update()

    def manejar_listar_usuarios(e):
        cargar_listado()

    def eliminar_usuario_en_archivo(id_eliminar: int):
        """
        Elimina el usuario del JSON usando repo.ruta_usuarios.
        Devuelve (ok: bool, mensaje: str).
        """
        # Leer JSON
        try:
            with open(repo.ruta_usuarios, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except FileNotFoundError:
            return False, "No se encontró el archivo de usuarios."
        except Exception as e:
            return False, f"Error al leer el archivo de usuarios: {e}"

        lista = datos.get("usuarios")
        if not isinstance(lista, list):
            return False, "El archivo de usuarios no tiene una lista 'usuarios' válida."

        # Buscar índice
        indice = -1
        for i, entrada in enumerate(lista):
            if isinstance(entrada, dict) and entrada.get("id_usuario") == id_eliminar:
                indice = i
                break

        if indice == -1:
            return False, f"No se ha encontrado ningún usuario con ID {id_eliminar}."

        # Eliminar y guardar
        del lista[indice]
        datos["usuarios"] = lista

        try:
            with open(repo.ruta_usuarios, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            return False, f"Error al guardar el archivo de usuarios: {e}"

        # Recargar en memoria
        try:
            repo.cargar_datos()
        except Exception:
            pass

        return True, f"Usuario con ID {id_eliminar} eliminado correctamente."

    def manejar_eliminar_usuario(e):
        valor = campo_id.value.strip()

        # Validar ID numérico
        if not valor.isdigit():
            mensaje_estado.value = "El ID debe ser un número entero."
            mensaje_estado.color = "red"
            page.update()
            return

        id_eliminar = int(valor)

        # Primera pulsación: pedir confirmación
        if (
            not estado_confirmacion["esperando"]
            or estado_confirmacion["id"] != id_eliminar
        ):
            estado_confirmacion["esperando"] = True
            estado_confirmacion["id"] = id_eliminar
            mensaje_estado.value = (
                f"Vuelve a pulsar 'Eliminar usuario por ID' para confirmar la "
                f"eliminación del usuario con ID {id_eliminar}."
            )
            mensaje_estado.color = "#FF9800"  # naranja
            page.update()
            return

        # Segunda pulsación: proceder al borrado
        estado_confirmacion["esperando"] = False
        ok, msg = eliminar_usuario_en_archivo(id_eliminar)

        mensaje_estado.value = msg
        mensaje_estado.color = "green" if ok else "red"

        if ok:
            cargar_listado()

        page.update()

    def manejar_volver(e):
        on_volver()

    boton_listar.on_click = manejar_listar_usuarios
    boton_eliminar.on_click = manejar_eliminar_usuario
    boton_volver.on_click = manejar_volver

    # ---------- TARJETA BLANCA CENTRAL ----------

    tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                titulo,
                subtitulo,
                separador_superior,
                ft.Container(height=10),
                boton_listar,
                ft.Container(height=20),
                etiqueta_eliminar,
                ft.Row([campo_id, boton_eliminar], spacing=10),
                ft.Container(height=10),
                ft.Text("Listado de usuarios:", size=14, weight=ft.FontWeight.BOLD),
                contenedor_listado,
                ft.Container(height=10),
                mensaje_estado,
                ft.Container(height=20),
                boton_volver,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        margin=30,
        bgcolor="white",
        border_radius=12,
        width=900,
        height=750,
    )

    # ---------- FONDO + TARJETA (mismo estilo que menú admin) ----------

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    controls=[tarjeta],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        ],
    )

    page.add(layout)
    page.update()
