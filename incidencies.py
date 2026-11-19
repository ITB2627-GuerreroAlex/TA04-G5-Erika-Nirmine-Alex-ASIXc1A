import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.theme import Theme
from playwright.sync_api import sync_playwright

TEXTOS_INCIDENCIAS = [
    "La pantalla se apaga intermitentemente al trabajar.",
    "El equipo tarda demasiado en iniciar sesión tras la actualización.",
    "Fallo de conexión a la red local tras el cambio de cable.",
    "Error de sincronización en Teams al intentar abrir archivos.",
    "Imposible imprimir documentos PDF en la impresora asignada.",
    "El ratón inalámbrico no responde y se desconecta solo."
]

console = Console(theme=Theme({"success": "bold green", "info": "bold cyan", "error": "bold red"}))

def mostrar_encabezado():
    console.clear()
    console.print(
        Panel.fit(
            "[bold white]🛠️ AUTOMATIZADOR DE INCIDENCIAS (PERFECCIONADO)[/bold white]\n"
            "[cyan]Manejo preciso de opciones normales y opción 'Altres:'[/cyan]",
            border_style="magenta",
            padding=(1, 4)
        )
    )

def solicitar_datos():
    url = Prompt.ask("[bold yellow]👉 Introduce la URL de tu formulario[/bold yellow]").strip()
    cantidad = IntPrompt.ask("[bold yellow]👉 ¿Cuántas respuestas deseas enviar?[/bold yellow]", default=5)
    modo_oculto = Confirm.ask("[bold yellow]👉 ¿Ejecutar en modo invisible?[/bold yellow]", default=False)
    return url, cantidad, modo_oculto

def procesar_formulario(page):
    preguntas = page.query_selector_all('div[role="listitem"]')

    for pregunta in preguntas:
        try:
            pregunta.scroll_into_view_if_needed()
            time.sleep(0.1)

            # 1. Campo de FECHA
            campo_fecha = pregunta.query_selector('input[type="date"]')
            if campo_fecha:
                dia = str(random.randint(1, 28)).zfill(2)
                mes = str(random.randint(1, 12)).zfill(2)
                fecha_iso = f"2026-{mes}-{dia}"
                
                campo_fecha.click(force=True)
                campo_fecha.fill(fecha_iso)
                time.sleep(0.2)
                continue

            # 2. Desplegables / Dropdowns
            desplegable = pregunta.query_selector('div[role="listbox"]')
            if desplegable:
                desplegable.click(force=True)
                time.sleep(0.3)
                for _ in range(random.randint(1, 3)):
                    page.keyboard.press("ArrowDown")
                    time.sleep(0.1)
                page.keyboard.press("Enter")
                time.sleep(0.3)
                continue

            # 3. Opciones de Selección (Radio / Checkbox)
            opciones = pregunta.query_selector_all('div[role="radio"], div[role="checkbox"]')
            if opciones:
                # Buscar si dentro de esta pregunta existe un campo de texto para "Altres:" / "Otro:"
                input_altres = pregunta.query_selector('input[type="text"][data-initial-value], input[aria-label*="Altre"], input[aria-label*="Otro"]')

                # Elegir una opción aleatoria entre todas las disponibles
                opcion_elegida = random.choice(opciones)

                # Verificar si la opción elegida es la que está vinculada a "Altres"
                # (Suele ser la última opción o la que contiene/envuelve el input_altres)
                es_opcion_altres = False
                if input_altres:
                    # Si el campo de texto está dentro del elemento de la opción elegida o si es la última opción
                    es_opcion_altres = (opcion_elegida == opciones[-1]) or ("altre" in opcion_elegida.inner_text().lower())

                if es_opcion_altres and input_altres:
                    # Si salió elegida 'Altres', hacemos clic directo en la casilla de texto y escribimos
                    input_altres.scroll_into_view_if_needed()
                    input_altres.click(force=True)
                    time.sleep(0.1)
                    input_altres.fill(random.choice(TEXTOS_INCIDENCIAS))
                    time.sleep(0.2)
                else:
                    # Si salió elegida una opción normal, solo hacemos clic en ella
                    opcion_elegida.click(force=True)
                    time.sleep(0.2)
                continue

            # 4. Preguntas de Texto Abierto principales (Respuesta corta / Párrafo)
            campos_texto = pregunta.query_selector_all('input[type="text"]:not([type="date"]), textarea')
            for campo in campos_texto:
                if campo.is_visible() and campo.is_enabled():
                    campo.fill(random.choice(TEXTOS_INCIDENCIAS))
                    time.sleep(0.2)

        except Exception:
            pass

    # 5. Enviar el formulario
    time.sleep(0.5)
    boton_enviar = page.query_selector(
        'div[role="button"]:has-text("Envia"), '
        'div[role="button"]:has-text("Enviar"), '
        'div[role="button"]:has-text("Submit"), '
        'span:has-text("Envia"), '
        'span:has-text("Enviar")'
    )

    if boton_enviar:
        boton_enviar.scroll_into_view_if_needed()
        boton_enviar.click(force=True)
    else:
        page.keyboard.press("Enter")
        
    time.sleep(2.5)

def ejecutar_script(url, cantidad, modo_oculto):
    console.print(f"\n[info]🚀 Procesando envíos...[/info]\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=modo_oculto)
        context = browser.new_context()
        page = context.new_page()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            tarea = progress.add_task("[cyan]Enviando respuestas...", total=cantidad)

            for i in range(cantidad):
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(1200)
                    
                    procesar_formulario(page)
                    
                    progress.update(tarea, advance=1, description=f"[cyan]Respuesta {i + 1}/{cantidad} enviada")
                    time.sleep(1.5)

                except Exception as e:
                    console.print(f"[error]✘ Error en el intento {i + 1}: {e}[/error]")

        browser.close()

    console.print(
        Panel(
            f"[success]✨ Proceso finalizado.[/success]\nSe han enviado las respuestas seleccionando 'Altres:' únicamente cuando correspondía.",
            border_style="green"
        )
    )

if __name__ == "__main__":
    mostrar_encabezado()
    url, cantidad, modo_oculto = solicitar_datos()
    ejecutar_script(url, cantidad, modo_oculto)