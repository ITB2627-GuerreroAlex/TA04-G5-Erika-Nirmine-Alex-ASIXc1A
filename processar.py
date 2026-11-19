import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
import textwrap
import json
import os

# Fixar el directori de treball a la carpeta on està aquest script
directorio_actual = os.path.dirname(os.path.abspath(__file__))
os.chdir(directorio_actual)

# Paleta de colors ANSI moderna i equilibrada
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[96m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
YELLOW  = "\033[93m"
WHITE   = "\033[97m"
RED     = "\033[91m"

PALETA_TAULES = [BLUE, MAGENTA, YELLOW, CYAN]

# Noms reals de les 11 preguntes/columnes del formulari d'incidències (per posició)
NOMS_PREGUNTES = [
    "Marca de temps (Any de la incidència)",
    "Correu electrònic / Usuari",
    "Nom i Cognoms",
    "Ubicació / Aula o Tipus d'Equip",
    "Descripció del problema / Avaria",
    "Nivell d'urgència / Prioritat",
    "Departament / Cicle formatiu",
    "Codi / Identificador d'equip",
    "Tècnic assignat",
    "Observacions addicionals",
    "Estat actual de la incidència"
]

def carregar_dades(xml_path):
    try:
        if not os.path.exists(xml_path):
            raise FileNotFoundError
        tree = ET.parse(xml_path)
        return tree.getroot()
    except FileNotFoundError:
        print(f"{RED}❌ Error: No s'ha trobat el fitxer XML a: {xml_path}{RESET}")
    except PermissionError:
        print(f"{RED}❌ Error: No tens permisos per llegir el fitxer XML.{RESET}")
    except ET.ParseError:
        print(f"{RED}❌ Error: El fitxer XML està corromput o té un format invàlid.{RESET}")
    except Exception:
        print(f"{RED}❌ Error inesperat en llegir el fitxer XML.{RESET}")
    return None

def obtenir_titol_pregunta(idx, child):
    """Obté el títol real de la pregunta usant atributs XML, etiqueta o la seva posició."""
    for attr in ("nom", "pregunta", "name", "label", "titol"):
        if attr in child.attrib and child.attrib[attr].strip():
            return child.attrib[attr].strip()

    tag = child.tag.strip()
    if tag.lower() not in ("campo", "camp", "col", "columna", "item", "field", "dada"):
        nom = tag.replace("_", " ").strip()
        return nom[0].upper() + nom[1:]

    if idx < len(NOMS_PREGUNTES):
        return NOMS_PREGUNTES[idx]
    return f"Pregunta #{idx + 1}"

def generar_barra(pct, color_accent, ample=15):
    """Genera una barra gràfica visual d'ample fix (15 caràcters) que mai descuadra la taula."""
    plens = int(round((pct / 100) * ample))
    buits = ample - plens
    return f"{color_accent}{'█' * plens}{DIM}{'░' * buits}{RESET}"

def imprimir_taula_pregunta(num_pregunta, titol_pregunta, comptador, total_valid, color_accent):
    """Dibuixa una taula completa per a una pregunta amb gràfic de barres visual."""
    ample_col1 = 42
    capcalera = f"TAULA {num_pregunta} · {titol_pregunta}"
    linies_titol = textwrap.wrap(capcalera, width=ample_col1) or [capcalera]

    print(f"\n{color_accent}╔{'═'*(ample_col1+2)}╦═════════╦═════════╦═════════════════╗{RESET}")
    for idx_t, linia_t in enumerate(linies_titol):
        col2_txt = f"{BOLD}Resp.{RESET}  " if idx_t == 0 else "       "
        col3_txt = f"{BOLD}Percent{RESET}" if idx_t == 0 else "       "
        col4_txt = f"{BOLD}Gràfic visual{RESET}  " if idx_t == 0 else "               "
        print(f"{color_accent}║{RESET} {BOLD}{WHITE}{linia_t:<{ample_col1}}{RESET} {color_accent}║{RESET} {col2_txt} {color_accent}║{RESET} {col3_txt} {color_accent}║{RESET} {col4_txt} {color_accent}║{RESET}")
    print(f"{color_accent}╠{'═'*(ample_col1+2)}╬═════════╬═════════╬═════════════════╣{RESET}")

    if total_valid == 0 or not comptador:
        barra_buida = generar_barra(0, color_accent)
        print(f"{color_accent}║{RESET} {DIM}{'Sense dades vàlides':<{ample_col1}}{RESET} {color_accent}║{RESET}       0 {color_accent}║{RESET}    0.0% {color_accent}║{RESET} {barra_buida} {color_accent}║{RESET}")
    else:
        elements = comptador.most_common(15)
        for pos, (resposta, quantitat) in enumerate(elements, start=1):
            pct = (quantitat / total_valid) * 100
            text_complet = f"#{pos} {resposta}"
            linies_resp = textwrap.wrap(text_complet, width=ample_col1) or [text_complet]
            barra = generar_barra(pct, color_accent)

            for idx_r, linia_r in enumerate(linies_resp):
                if pos == 1:
                    estil_text = f"{BOLD}{color_accent}{linia_r:<{ample_col1}}{RESET}"
                    estil_num  = f"{BOLD}{color_accent}{quantitat:>7}{RESET}" if idx_r == 0 else "       "
                    estil_pct  = f"{BOLD}{color_accent}{pct:>6.1f}%{RESET}" if idx_r == 0 else "       "
                else:
                    estil_text = f"{WHITE}{linia_r:<{ample_col1}}{RESET}"
                    estil_num  = f"{quantitat:>7}" if idx_r == 0 else "       "
                    estil_pct  = f"{DIM}{pct:>6.1f}%{RESET}" if idx_r == 0 else "       "

                col_grafic = barra if idx_r == 0 else "               "
                print(f"{color_accent}║{RESET} {estil_text} {color_accent}║{RESET} {estil_num} {color_accent}║{RESET} {estil_pct} {color_accent}║{RESET} {col_grafic} {color_accent}║{RESET}")

        restants = len(comptador) - len(elements)
        if restants > 0:
            nota = f"... i {restants} respostes diferents més"
            print(f"{color_accent}╟{'─'*(ample_col1+2)}╫─────────╫─────────╫─────────────────╢{RESET}")
            print(f"{color_accent}║{RESET} {DIM}{nota:<{ample_col1}}{RESET} {color_accent}║{RESET} {'':>7} {color_accent}║{RESET} {'':>7} {color_accent}║{RESET} {'':>15} {color_accent}║{RESET}")

    print(f"{color_accent}╚{'═'*(ample_col1+2)}╩═════════╩═════════╩═════════════════╝{RESET}")

def desar_en_json(incidencies_valides, resum_estadistic, json_path="incidencies.json"):
    """Exercici 4: Desa la informació en JSON controlant existència, sobreescriptura i duplicats."""
    print(f"\n{CYAN}╔═══════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{RESET} {BOLD}{WHITE}                   EMMAGATZEMATGE EN FORMAT JSON (incidencies.json)                 {RESET}{CYAN}║{RESET}")
    print(f"{CYAN}╚═══════════════════════════════════════════════════════════════════════════════════╝{RESET}")

    if not os.path.exists(json_path):
        dades_a_desar = {
            "resum_estadistic": resum_estadistic,
            "total_incidencies": len(incidencies_valides),
            "incidencies": incidencies_valides
        }
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dades_a_desar, f, indent=4, ensure_ascii=False)
            print(f"{CYAN}✨ Fitxer '{json_path}' creat correctament amb {len(incidencies_valides)} incidències.{RESET}")
        except PermissionError:
            print(f"{RED}❌ Error de permisos: No es pot crear el fitxer '{json_path}'.{RESET}")
        except Exception as e:
            print(f"{RED}❌ Error inesperat en desar el JSON: {e}{RESET}")
        return

    print(f"{YELLOW}⚠️ El fitxer '{json_path}' ja existeix.{RESET}")
    print(f"  {BOLD}1.{RESET} Sobreescriure'l (esborra el contingut anterior i escriu les dades de nou)")
    print(f"  {BOLD}2.{RESET} Afegir les noves incidències (conserva les existents i evita duplicats per ID)")

    while True:
        try:
            opcio = input(f"{BOLD}{CYAN}👉 Què vols fer? (1/2): {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Operació cancel·lada.{RESET}")
            return

        if opcio == "1":
            dades_a_desar = {
                "resum_estadistic": resum_estadistic,
                "total_incidencies": len(incidencies_valides),
                "incidencies": incidencies_valides
            }
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(dades_a_desar, f, indent=4, ensure_ascii=False)
                print(f"{CYAN}✨ Fitxer '{json_path}' sobreescrit amb èxit ({len(incidencies_valides)} incidències).{RESET}")
            except PermissionError:
                print(f"{RED}❌ Error de permisos: No es pot sobreescriure '{json_path}'.{RESET}")
            except Exception as e:
                print(f"{RED}❌ Error en sobreescriure el JSON: {e}{RESET}")
            break

        elif opcio == "2":
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    contingut_existent = json.load(f)

                if isinstance(contingut_existent, dict) and "incidencies" in contingut_existent:
                    llista_previa = contingut_existent["incidencies"]
                elif isinstance(contingut_existent, list):
                    llista_previa = contingut_existent
                else:
                    llista_previa = []

            except (json.JSONDecodeError, UnicodeDecodeError):
                print(f"{RED}⚠️ Avís: El fitxer JSON existent estava corromput. Es regenerarà de zero.{RESET}")
                llista_previa = []
            except PermissionError:
                print(f"{RED}❌ Error de permisos: No es pot llegir '{json_path}'.{RESET}")
                return

            ids_existents = {str(item["id"]) for item in llista_previa if isinstance(item, dict) and "id" in item}
            noves_afegides = 0
            duplicades_evitades = 0

            for inc in incidencies_valides:
                id_actual = str(inc.get("id", ""))
                if id_actual and id_actual not in ids_existents:
                    llista_previa.append(inc)
                    ids_existents.add(id_actual)
                    noves_afegides += 1
                else:
                    duplicades_evitades += 1

            dades_actualitzades = {
                "resum_estadistic": resum_estadistic,
                "total_incidencies": len(llista_previa),
                "incidencies": llista_previa
            }

            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(dades_actualitzades, f, indent=4, ensure_ascii=False)
                print(f"{CYAN}✨ Actualització completada a '{json_path}':{RESET}")
                print(f"   • Noves incidències afegides : {BOLD}{CYAN}{noves_afegides}{RESET}")
                print(f"   • Duplicades evitades (ID)   : {DIM}{duplicades_evitades}{RESET}")
                print(f"   • Total al fitxer JSON       : {BOLD}{len(llista_previa)}{RESET}")
            except PermissionError:
                print(f"{RED}❌ Error de permisos: No es pot escriure a '{json_path}'.{RESET}")
            except Exception as e:
                print(f"{RED}❌ Error en actualitzar el JSON: {e}{RESET}")
            break
        else:
            print(f"{RED}⚠️ Opció no vàlida. Escriu 1 per sobreescriure o 2 per afegir noves.{RESET}")

def processar_incidencies(xml_path):
    root = carregar_dades(xml_path)
    if root is None:
        return

    total_registres = 0
    incidencies_valides = []
    incidencies_erronies = 0
    anys_descartats = []
    any_actual = datetime.now().year

    comptadors_per_columna = {}
    titols_per_columna = {}

    for idx_reg, inc in enumerate(root, start=1):
        total_registres += 1
        children = list(inc)
        data_text = ""
        id_trobat = None
        detall_camps = {}

        for idx_col, child in enumerate(children):
            val = child.text.strip() if child.text else ""
            titol_col = obtenir_titol_pregunta(idx_col, child)
            titols_per_columna[idx_col] = titol_col
            detall_camps[titol_col] = val

            if idx_col == 0 or 'temps' in titol_col.lower() or 'data' in titol_col.lower():
                if any(c.isdigit() for c in val) and ('/' in val or '-' in val):
                    data_text = val
            if titol_col.lower() == 'id' and val:
                id_trobat = val

        # Filtratge de dates errònies (ex: 2064)
        es_valida = True
        any_extret = None
        if data_text:
            try:
                parts = data_text.replace('-', '/').split('/')
                for p in parts:
                    num = int(p.split()[0])
                    if num > 1900:
                        if num > any_actual or num < 2000:
                            es_valida = False
                            anys_descartats.append(str(num))
                        else:
                            any_extret = str(num)
                        break
            except (IndexError, ValueError):
                pass

        if not es_valida:
            incidencies_erronies += 1
            continue

        for idx_col, child in enumerate(children):
            val = child.text.strip() if child.text else ""
            if idx_col not in comptadors_per_columna:
                comptadors_per_columna[idx_col] = Counter()

            if idx_col == 0 and any_extret:
                valor_estadistic = any_extret
            else:
                valor_estadistic = val if val else "(Sense resposta)"

            comptadors_per_columna[idx_col][valor_estadistic] += 1

        registre_final = {"id": id_trobat if id_trobat else f"INC-{idx_reg:04d}"}
        registre_final.update(detall_camps)
        incidencies_valides.append(registre_final)

    if total_registres == 0:
        print(f"{RED}❌ Error: El fitxer XML està buit.{RESET}")
        return

    total_v = len(incidencies_valides)
    pct_valides = (total_v / total_registres) * 100
    pct_erronies = (incidencies_erronies / total_registres) * 100

    # CAPÇALERA PRINCIPAL
    print(f"\n{CYAN}╔═══════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{RESET} {BOLD}{WHITE}              SISTEMA D'ANÀLISI D'INCIDÈNCIES TÈCNIQUES · ITB2627-MDS               {RESET}{CYAN}║{RESET}")
    print(f"{CYAN}╚═══════════════════════════════════════════════════════════════════════════════════╝{RESET}")

    # TAULA RESUM DE NETEJA DE DADES
    print(f"\n{CYAN}╔════════════════════════════════════════════════════════╦═══════════╦══════════════╗{RESET}")
    print(f"{CYAN}║{RESET} {BOLD}{WHITE}{'RESUM DE NETEJA I QUALITAT DE DADES':<54}{RESET} {CYAN}║{RESET} {BOLD}Registres{RESET} {CYAN}║{RESET} {BOLD}Percentatge{RESET}  {CYAN}║{RESET}")
    print(f"{CYAN}╠════════════════════════════════════════════════════════╬═══════════╬══════════════╣{RESET}")
    print(f"{CYAN}║{RESET} {WHITE}{'Total registres llegits de l\'XML':<54}{RESET} {CYAN}║{RESET} {BOLD}{total_registres:>9}{RESET} {CYAN}║{RESET}       100.0% {CYAN}║{RESET}")
    print(f"{CYAN}║{RESET} {CYAN}{'Incidències vàlides (dades netes)':<54}{RESET} {CYAN}║{RESET} {BOLD}{CYAN}{total_v:>9}{RESET} {CYAN}║{RESET} {CYAN}{pct_valides:>11.1f}%{RESET} {CYAN}║{RESET}")
    print(f"{CYAN}║{RESET} {RED}{'Incidències descartades (dates errònies)':<54}{RESET} {CYAN}║{RESET} {BOLD}{RED}{incidencies_erronies:>9}{RESET} {CYAN}║{RESET} {RED}{pct_erronies:>11.1f}%{RESET} {CYAN}║{RESET}")
    print(f"{CYAN}╚════════════════════════════════════════════════════════╩═══════════╩══════════════╝{RESET}")

    # UNA TAULA AMB GRÀFIC VISUAL PER A CADA PREGUNTA
    columnes_ordenades = sorted(comptadors_per_columna.keys())
    for num_taula, idx_col in enumerate(columnes_ordenades, start=1):
        color = PALETA_TAULES[(num_taula - 1) % len(PALETA_TAULES)]
        titol = titols_per_columna[idx_col]
        imprimir_taula_pregunta(num_taula, titol, comptadors_per_columna[idx_col], total_v, color)

    # CONCLUSIONS CLAU PER A CADA PREGUNTA
    if total_v > 0 and columnes_ordenades:
        print(f"\n{YELLOW}╔═══════════════════════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{YELLOW}║{RESET} {BOLD}{YELLOW}💡 CONCLUSIONS CLAU DE L'ANÀLISI (RESPOSTA MAJORITÀRIA PER PREGUNTA){RESET}                {YELLOW}║{RESET}")
        print(f"{YELLOW}╠═══════════════════════════════════════════════════════════════════════════════════╣{RESET}")
        for num_taula, idx_col in enumerate(columnes_ordenades, start=1):
            titol = titols_per_columna[idx_col]
            top_val, count_val = comptadors_per_columna[idx_col].most_common(1)[0]
            pct_val = (count_val / total_v) * 100
            preg_curta = (titol[:32] + "..") if len(titol) > 34 else titol
            val_curt = (top_val[:28] + "..") if len(top_val) > 30 else top_val
            print(f"{YELLOW}║{RESET}  {BOLD}P{num_taula}.{RESET} {preg_curta}: {CYAN}{val_curt}{RESET} ({pct_val:.1f}% · {count_val})")
        if incidencies_erronies > 0:
            exemples = ", ".join(sorted(set(anys_descartats))[:3])
            print(f"{YELLOW}║{RESET}  {BOLD}Neteja:{RESET} S'han filtrat {RED}{incidencies_erronies}{RESET} registres amb anys invàlids ({exemples}).")
        print(f"{YELLOW}╚═══════════════════════════════════════════════════════════════════════════════════╝{RESET}")

    # EXERCICI 4: DESAR EN JSON (incidencies.json)
    if total_v > 0:
        resum_json = {
            "total_registres_xml": total_registres,
            "incidencies_valides": total_v,
            "incidencies_descartades": incidencies_erronies,
            "estadistiques_per_pregunta": {
                titols_per_columna[idx]: dict(comptadors_per_columna[idx].most_common())
                for idx in columnes_ordenades
            }
        }
        desar_en_json(incidencies_valides, resum_json, "incidencies.json")

    # PREGUNTA FINAL PER VEURE ELS REGISTRES DETALLATS
    if total_v > 0:
        print()
        try:
            resposta = input(f"{BOLD}{CYAN}Vols que t'ensenyi totes les respostes detallades? (s/n): {RESET}").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Sortint del programa...{RESET}")
            return

        if resposta in ("s", "si", "sí"):
            print(f"\n{BOLD}{CYAN}═══ LLISTAT DETALLAT DE LES {total_v} INCIDÈNCIES VÀLIDES ═══{RESET}")
            for i, camps in enumerate(incidencies_valides, start=1):
                print(f"\n{BLUE}┌───────────────────────────────────────────────────────────────────────────────────┐{RESET}")
                print(f"{BLUE}│{RESET} {BOLD}{CYAN}Registre #{i} (ID: {camps['id']}){RESET}" + " "*(64 - len(str(i)) - len(str(camps['id']))) + f"{BLUE}│{RESET}")
                print(f"{BLUE}├───────────────────────────────────────────────────────────────────────────────────┤{RESET}")
                for clau, valor in camps.items():
                    if clau == "id":
                        continue
                    val_net = valor if valor else f"{DIM}(Sense resposta){RESET}"
                    print(f"  {BOLD}{WHITE}{clau}:{RESET} {val_net}")
                print(f"{BLUE}└───────────────────────────────────────────────────────────────────────────────────┘{RESET}")
        else:
            print(f"{DIM}D'acord, no es mostren les respostes individuals. Procés finalitzat.{RESET}\n")

if __name__ == "__main__":
    ruta_xml = "Conversorxml/_incidencies.xml" if os.path.exists("Conversorxml/_incidencies.xml") else "incidencies.xml"
    processar_incidencies(ruta_xml)