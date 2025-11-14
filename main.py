from machine import Pin, PWM
from neopixel import NeoPixel
from time import sleep

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

def is_button_pressed():
    """Prüft ob Button gerade gedrückt ist (für schnelle Interrupt-Checks)

    Returns:
        True wenn Button gedrückt ist, False sonst
    """
    global last_button_state
    button_state = button.value()

    # Button wurde gedrückt (Flanke 1 -> 0)
    if last_button_state == 1 and button_state == 0:
        last_button_state = button_state
        return True

    last_button_state = button_state
    return False

def handle_button_press():
    """Behandelt Button-Druck und spielt Musik"""
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

try:
    # Initialisierung
    neopixel_eyes.clear_all()
    sleep(0.5)

    # Button-Status einlesen (nicht annehmen!)
    last_button_state = button.value()
    print(f"Initialer Button-Status: {last_button_state}")
    sleep(0.1)  # Kurz warten für Stabilisierung

    # Interrupt-Check-Funktion an neopixel_eyes übergeben
    neopixel_eyes.interrupt_check = is_button_pressed

    while True:
        # Führe Animation aus (wird automatisch unterbrochen bei Button-Druck)
        interrupted = neopixel_eyes.do_animation()

        # Wenn Animation durch Button unterbrochen wurde
        if interrupted:
            handle_button_press()
            # Button-Status neu einlesen nach Musik
            last_button_state = button.value()
            continue

        # Kurze Pause zwischen Animationen (auch interruptible)
        pause_duration = 0.5
        interval = 0.05
        elapsed = 0.0

        while elapsed < pause_duration:
            if is_button_pressed():
                handle_button_press()
                last_button_state = button.value()
                break
            sleep(interval)
            elapsed += interval

except KeyboardInterrupt:
    buzzer_obj.duty_u16(0)
    buzzer_obj.deinit()
    neopixel_eyes.clear_all()
    print("\n\nBeendet - Frohe Weihnachten!")
