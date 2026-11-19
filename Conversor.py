
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import os


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def limpiar_ruta(texto):
    return Path(texto.strip().strip('"').strip("'")).expanduser()


def comprobar_formato_csv(ruta):

    try:
        with open(ruta, "rb") as fichero:
            primeros_bytes = fichero.read(8192)

        # Comprobar si esta vaciop
        if not primeros_bytes:
            return False

        # Comprobar archivos ZIP
        if primeros_bytes.startswith(b"PK"):
            return False

        # Comprobar archivos PDF
        if primeros_bytes.startswith(b"%PDF"):
            return False

        # Comprobar imagen JPEG
        if primeros_bytes.startswith(b"\xff\xd8\xff"):
            return False

        # Comprobar imagen PNG
        if primeros_bytes.startswith(b"\x89PNG"):
            return False

        # Comprobar imagen GIF
        if primeros_bytes.startswith((b"GIF87a", b"GIF89a")):
            return False

        # Comprobar ejecutables Windows
        if primeros_bytes.startswith(b"MZ"):
            return False

        # Comprobar archivos binarios
        if b"\x00" in primeros_bytes:
            return False

        return True

    except OSError:
        return False


# ==========================================
# BUSCAR INCIDENCIES.CSV
# ==========================================

def buscar_incidencies():

    print("\nBuscando incidencies.csv en el ordenador...")
    print("Esto puede tardar unos minutos.\n")

    archivos = []

    if os.name == "nt":

        unidades = [
            Path(f"{letra}:\\")
            for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if Path(f"{letra}:\\").exists()
        ]

    else:
        unidades = [Path.home()]

    carpetas_excluidas = {
        "Windows",
        "Program Files",
        "Program Files (x86)",
        "$Recycle.Bin",
        "System Volume Information"
    }

    for unidad in unidades:

        for ruta, carpetas, ficheros in os.walk(unidad):

            carpetas[:] = [
                carpeta for carpeta in carpetas
                if carpeta not in carpetas_excluidas
            ]

            for fichero in ficheros:

                if fichero.lower() == "incidencies.csv":
                    archivos.append(Path(ruta) / fichero)

    return sorted(archivos, key=lambda x: str(x).lower())


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def convertir():

    print("\n========================================")
    print("          CONVERSOR CSV A XML")
    print("========================================")

    print("\nEste programa convierte exclusivamente:")
    print("incidencies.csv -> incidencies.xml")

    # 1. BUSCAR ARCHIVOS

    archivos = buscar_incidencies()

    if not archivos:

        print("\n[ERROR] No se ha encontrado incidencies.csv.")
        print("Comprueba que el archivo existe en el ordenador.")

        return

    print(f"\n[OK] Archivos encontrados: {len(archivos)}")

    # 2. SELECCIONAR ARCHIVO SI HAY VARIOS

    if len(archivos) == 1:

        ruta_csv = archivos[0]

        print("\n[OK] Se ha encontrado un unico archivo.")
        print(f"Ubicacion: {ruta_csv}")

    else:

        print("\nSe han encontrado varios archivos incidencies.csv:\n")

        for i, archivo in enumerate(archivos, start=1):

            print(f"{i}. {archivo}")
        
        while True:

            opcion = input(
                "\n¿Qué archivo quieres convertir? Escribe su numero: "
            ).strip()

            try:

                numero = int(opcion)

                if 1 <= numero <= len(archivos):

                    ruta_csv = archivos[numero - 1]
                    break

                print("\n[ERROR] Selecciona un numero de la lista.")

            except ValueError:

                print("\n[ERROR] Debes escribir solamente un numero.")

    # 3. COMPROBAR FORMATO DEL ARCHIVO

    print("\nComprobando el formato del archivo...")

    if not comprobar_formato_csv(ruta_csv):

        print("\n[ERROR] El archivo incidencies.csv no tiene un formato CSV válido.")
        print("El contenido del archivo no corresponde con un CSV legible.")
        print("Comprueba que no esté comprimido o tenga una extensión incorrecta.")

        return

    print("[OK] El formato inicial del archivo es correcto.")

    # 4. DETECTAR CODIFICACION

    codificacion = None

    for encoding in ["utf-8-sig", "utf-8", "cp1252", "latin-1"]:

        try:

            with open(ruta_csv, "r", encoding=encoding) as fichero:
                fichero.read()

            codificacion = encoding
            break

        except UnicodeDecodeError:
            continue

    if codificacion is None:

        print("\n[ERROR] No se puede leer la codificacion del archivo.")
        return

    # 5. DETECTAR SEPARADOR

    try:

        with open(ruta_csv, "r", encoding=codificacion) as fichero:
            muestra = fichero.read(8192)

        try:

            separador = csv.Sniffer().sniff(
                muestra,
                delimiters=",;\t|"
            ).delimiter

        except csv.Error:

            separador = ","

    except OSError:

        print("\n[ERROR] No se puede acceder al archivo CSV.")
        return

    # 6. LEER Y CONVERTIR EL CSV

    raiz = ET.Element("respuestas")
    total = 0

    try:

        with open(
            ruta_csv,
            "r",
            encoding=codificacion,
            newline=""
        ) as fichero:

            lector = csv.reader(
                fichero,
                delimiter=separador
            )

            encabezados = next(lector, None)

            if not encabezados or not any(encabezados):

                print("\n[ERROR] El CSV esta vacio o no tiene encabezados.")
                return

            for numero_fila, fila in enumerate(lector, start=2):

                if not fila or all(valor == "" for valor in fila):
                    continue

                if len(fila) != len(encabezados):

                    print(f"\n[ERROR] Problema en la fila {numero_fila}.")
                    print("El numero de columnas no coincide.")
                    print("No se ha generado ningun XML.")

                    return

                total += 1

                respuesta = ET.SubElement(
                    raiz,
                    "respuesta",
                    id=str(total)
                )

                for nombre, valor in zip(encabezados, fila):

                    campo = ET.SubElement(
                        respuesta,
                        "campo",
                        nombre=nombre
                    )

                    campo.text = valor

    except PermissionError:

        print("\n[ERROR] No tienes permiso para leer el CSV.")
        return

    except OSError:

        print("\n[ERROR] No se ha podido abrir el CSV.")
        return

    except csv.Error:

        print("\n[ERROR] El formato del CSV no es valido.")
        return

    if total == 0:

        print("\n[ERROR] El CSV no contiene respuestas.")
        return

    print("\n[OK] CSV leido correctamente.")
    print(f"[OK] Respuestas encontradas: {total}")

    # 7. ELEGIR UBICACION DEL XML

    carpeta_programa = Path(__file__).resolve().parent

    print("\n========================================")
    print("          GUARDAR ARCHIVO XML")
    print("========================================")

    print("\n¿Donde quieres guardar incidencies.xml?")
    print("1. En la misma carpeta que incidencies.csv.")
    print("2. En la misma carpeta que el programa Python.")
    print("3. Elegir otra carpeta.")

    while True:

        opcion = input(
            "\nSelecciona una opcion (1/2/3): "
        ).strip()

        if opcion == "1":

            ruta_xml = ruta_csv.parent / "incidencies.xml"
            break

        elif opcion == "2":

            ruta_xml = carpeta_programa / "incidencies.xml"
            break

        elif opcion == "3":

            destino = input(
                "\nEscribe la ruta de la carpeta donde guardarlo: "
            ).strip()

            if not destino:

                print("\n[ERROR] No has indicado ninguna ubicacion.")
                continue

            carpeta_destino = limpiar_ruta(destino)

            if not carpeta_destino.is_dir():

                print("\n[ERROR] No he encontrado esa carpeta.")
                continue

            ruta_xml = carpeta_destino / "incidencies.xml"
            break

        else:

            print("\n[ERROR] Selecciona 1, 2 o 3.")

    # 8. COMPROBAR SI EL XML YA EXISTE

    if ruta_xml.exists():

        confirmar = input(
            "\nEl archivo incidencies.xml ya existe."
            "\n¿Quieres sustituirlo? (s/n): "
        ).strip().lower()

        if confirmar != "s":

            print("\nOperacion cancelada.")
            return

    # 9. GENERAR Y GUARDAR XML

    try:

        arbol = ET.ElementTree(raiz)

        ET.indent(arbol, space="    ")

        arbol.write(
            ruta_xml,
            encoding="utf-8",
            xml_declaration=True
        )

        # 10. VERIFICACION FINAL

        comprobacion = ET.parse(ruta_xml)

        registros = comprobacion.getroot().findall("respuesta")

        if len(registros) != total:

            print("\n[ERROR] La comprobacion final ha fallado.")
            return

        # 11. RESULTADO FINAL

        print("\n========================================")
        print("       CONVERSION COMPLETADA")
        print("========================================")

        print("\n¡Todo ha salido correctamente!")

        print("\nArchivo original: incidencies.csv")
        print(f"Respuestas convertidas: {total}")
        print("Archivo XML creado: incidencies.xml")
        print(f"Ubicacion: {ruta_xml.resolve()}")

        print("\nEl archivo XML esta listo para utilizarse.")

    except PermissionError:

        print("\n[ERROR] No tienes permiso para guardar el XML.")

    except OSError:

        print("\n[ERROR] No se ha podido guardar el archivo XML.")

    except Exception:

        print("\n[ERROR] Ha ocurrido un problema inesperado.")
        print("Comprueba el archivo e intentalo de nuevo.")


# ==========================================
# INICIAR PROGRAMA
# ==========================================

if __name__ == "__main__":

    try:

        convertir()

    except KeyboardInterrupt:

        print("\n\nOperacion cancelada por el usuario.")

    except Exception:

        print("\n[ERROR] No se ha podido completar el programa.")
        print("Vuelve a intentarlo.")
