
from time import sleep
import random

# COLORS
R = "\033[0m"
B = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"


def animacio_cuinar():

    punts = 0

    print("\n" * 2)
    print(PURPLE + B + """
╔══════════════════════════════════════╗
║                                      ║
║       🍜 YAKISOBA MASTER CHEF 🍜     ║
║                                      ║
║           MODE INTERACTIU            ║
║                                      ║
╚══════════════════════════════════════╝
""" + R)

    print(YELLOW + "\n👨‍🍳 AVUI TU ETS EL XEF!")
    print("Has de preparar un Yakisoba perfecte.")
    print("Aconsegueix la maxima puntuacio!\n" + R)

    input("Prem ENTER per començar...")

    # FASE 1: FOC
    print("\n" + RED + "🔥 FASE 1: ENCEN ELS FOGONS" + R)

    resposta = input("Escriu 'encendre' per activar el foc: ").lower()

    if resposta == "encendre":
        print(GREEN + "🔥 PERFECTE! FOGONS ACTIVATS!" + R)
        punts += 25
    else:
        print(YELLOW + "El foc ja està encès... continuem!" + R)
        punts += 10

    sleep(1)

    # FASE 2: INGREDIENTS
    print("\n" + BLUE + "🥕 FASE 2: PREPARAR INGREDIENTS" + R)

    print("""
Quin ingredient vols posar primer?

1. Pastanagues 🥕
2. Fideus 🍜
3. Salsa 🥢
""")

    resposta = input("Tria 1, 2 o 3: ")

    if resposta == "1":
        print(GREEN + "Molt bé! Les pastanagues estan preparades!" + R)
        punts += 25

    elif resposta == "2":
        print(YELLOW + "Els fideus encara no! Però continuem!" + R)
        punts += 10

    elif resposta == "3":
        print(YELLOW + "La salsa arribarà més tard!" + R)
        punts += 10

    else:
        print(RED + "No has triat cap ingredient correcte." + R)

    sleep(1)

    # FASE 3: CUINAR
    print("\n" + YELLOW + "🍳 FASE 3: A CUINAR!" + R)

    print("La paella està calenta!")
    print("Has de remoure els ingredients 3 vegades.")

    for i in range(3):

        input("\nPrem ENTER per remoure la paella...")

        print("🥄 Remenant" + "." * (i + 1))
        sleep(0.5)

    print(GREEN + "\nMOLT BÉ! ELS INGREDIENTS ESTAN BARREJATS!" + R)
    punts += 25

    sleep(1)

    # FASE 4: SERVIR
    print("\n" + PURPLE + "🥢 FASE 4: SERVIR EL YAKISOBA" + R)

    print("""
Creus que el plat ja està preparat?

1. Sí, servir!
2. No, continuar cuinant.
""")

    resposta = input("Quina és la teva decisió? ")

    if resposta == "1":
        print(GREEN + "🍜 PLAT SERVIT CORRECTAMENT!" + R)
        punts += 25

    else:
        print(YELLOW + "Has cuinat una mica més. Ara ja està llest!" + R)
        punts += 15

    sleep(1)

    # RESULTAT FINAL
    print("\n")
    print(YELLOW + B + """
╔══════════════════════════════════════╗
║                                      ║
║          🏆 FINAL DEL JOC 🏆        ║
║                                      ║
╚══════════════════════════════════════╝
""" + R)

    print(CYAN + "      ⭐ PUNTUACIÓ: " + str(punts) + "/100" + R)

    if punts >= 85:
        print(GREEN + B + "\n🏆 ELSPECIALISTA EN YAKISOBA!" + R)

    elif punts >= 60:
        print(YELLOW + "\n👏 BON CUINER! HAS FET UNA BONA FEINA!" + R)

    else:
        print(RED + "\n👨‍🍳 NECESSITES UNA MICA MÉS DE PRÀCTICA!" + R)

    print("\n🍜🥢🍜 BON PROFIT! 😋")


# INICI DEL JOC
animacio_cuinar()

