from machine import Pin, PWM
from neopixel import NeoPixel
from time import sleep
import random

# Module importieren
import neopixel_eyes
import christmas_light_show

# Hardware initialisieren (beide Module teilen sich das NeoPixel)
neopixel_pin = Pin(1, Pin.OUT)
np = NeoPixel(neopixel_pin, 12)
buzzer_obj = PWM(Pin(8))

# Hardware an beide Module übergeben
neopixel_eyes.np = np
christmas_light_show.init_hardware(neopixel_obj=np, buzzer_obj=buzzer_obj)

# Sicherstellen, dass alle LEDs aus sind und brightness zurückgesetzt ist
christmas_light_show.current_brightness = 0
for i in range(12):
    np[i] = (0, 0, 0)
np.write()

# Button-Konfiguration
button = Pin(21, Pin.IN, Pin.PULL_UP)  # GP21 mit internem Pull-Up

print("\n" + "="*40)
print("  WEIHNACHTS-ROBOTER")
print("="*40)
print("NeoPixel: GP1 (2x 12 LEDs)")
print("Buzzer: GP8")
print("Button: GP21")
print("")
print("Modus: Augen-Animation")
print("Button drücken -> Zufälliges Lied")
print("Drücke Strg+C zum Beenden")
print("="*40 + "\n")

def check_button():
    """Prüft ob Button gedrückt wurde und spielt ggf. Musik"""
    global last_button_state
    button_state = button.value()

    # Button wurde gedrückt (Flanke 1 -> 0)
    if last_button_state == 1 and button_state == 0:
        print("\n>>> Button gedrückt! <<<")
        print("Wechsel zu Musik-Modus...\n")

        # Augen ausschalten
        neopixel_eyes.clear_all()
        sleep(0.2)

        # Zufälliges Lied abspielen
        christmas_light_show.play_random_song()

        # Kleine Pause
        sleep(1)

        # Zurück zum Augen-Modus
        print("\nZurück zum Augen-Modus\n")

        last_button_state = button.value()  # Status neu einlesen
        return True

    last_button_state = button_state
    return False

try:
    # Initialisierung
    neopixel_eyes.clear_all()
    sleep(0.5)

    # Button-Status einlesen (nicht annehmen!)
    last_button_state = button.value()
    print(f"Initialer Button-Status: {last_button_state}")
    sleep(0.1)  # Kurz warten für Stabilisierung

    while True:
        # Button prüfen
        if check_button():
            continue

        # Zufällige Pause vor der Aktion (1-3 Sekunden)
        sleep(random.uniform(1.0, 3.0))

        # Button prüfen
        if check_button():
            continue

        # Eine Animation ausführen (mit integrierter Zufälligkeit)
        neopixel_eyes.do_animation()

        # Button prüfen
        if check_button():
            continue

        # Kurze Pause zwischen Animationen
        sleep(0.5)

        # Button prüfen
        if check_button():
            continue

except KeyboardInterrupt:
    buzzer_obj.duty_u16(0)
    buzzer_obj.deinit()
    neopixel_eyes.clear_all()
    print("\n\nBeendet - Frohe Weihnachten!")
