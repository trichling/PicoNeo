from machine import Pin
from time import sleep

# Button-Konfiguration
button = Pin(21, Pin.IN, Pin.PULL_UP)  # GP20 mit internem Pull-Up

print("\n" + "="*40)
print("  BUTTON TEST")
print("="*40)
print("Button: GP20")
print("Verkabelung: Button zwischen GP20 und GND")
print("")
print("Drücke den Button zum Testen...")
print("Drücke Strg+C zum Beenden")
print("="*40 + "\n")

try:
    last_state = button.value()
    print(f"Start-Status: {last_state} (1=nicht gedrückt, 0=gedrückt)")

    while True:
        current_state = button.value()

        # Status hat sich geändert
        if current_state != last_state:
            if current_state == 0:
                print(">>> Button GEDRÜCKT (0) <<<")
            else:
                print(">>> Button LOSGELASSEN (1) <<<")

            last_state = current_state

        # Kontinuierliche Status-Anzeige alle 2 Sekunden
        sleep(0.1)

except KeyboardInterrupt:
    print("\n\nTest beendet!")
    print(f"Letzter Status: {button.value()}")
