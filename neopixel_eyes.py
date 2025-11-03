from machine import Pin
from neopixel import NeoPixel
from time import sleep

# Hardware-Konfiguration
NUM_LEDS = 12  # Anzahl LEDs pro Ring (beide Ringe parallel geschaltet)
neopixel_pin = Pin(1, Pin.OUT)  # GP1 für NeoPixel
np = NeoPixel(neopixel_pin, NUM_LEDS)

# Farbe für die Augen (weiß für offenes Auge)
EYE_COLOR = (255, 255, 255)  # RGB Weiß
EYE_BRIGHTNESS = 0.01  # 1% Helligkeit
OFF = (0, 0, 0)

def scale_color(color, brightness):
    """Skaliert eine Farbe mit Helligkeitsfaktor"""
    return tuple(int(c * brightness) for c in color)

def clear_all():
    """Schaltet alle LEDs aus"""
    for i in range(NUM_LEDS):
        np[i] = OFF
    np.write()

def get_upper_half():
    """Gibt die LED-Indizes für die obere Hälfte zurück (Auge offen)"""
    # Bei 12 LEDs: LED 0 ist oben, dann im Uhrzeigersinn
    # Obere Hälfte: LEDs 9, 10, 11, 0, 1, 2, 3
    quarter = NUM_LEDS // 4 

    # Von links-oben über oben nach rechts-oben
    upper = []
    for i in range(NUM_LEDS):
        # Obere Hälfte: von 9 bis 3 (bei 12 LEDs)
        if i >= NUM_LEDS - quarter or i <= quarter:
            upper.append(i)
    return upper

def get_lower_half():
    """Gibt die LED-Indizes für die untere Hälfte zurück"""
    # Untere Hälfte: LEDs 4, 5, 6, 7, 8
    quarter = NUM_LEDS // 4
    three_quarter = NUM_LEDS * 3 // 4

    lower = []
    for i in range(quarter + 1, three_quarter):
        lower.append(i)
    return lower

def get_left_quarter():
    """LEDs für linkes Viertel (oben links) - die beim Links-Schauen ausgehen"""
    # Bei 12 LEDs: 9, 10, 11 (3 LEDs)
    quarter = NUM_LEDS // 4
    return list(range(NUM_LEDS - quarter, NUM_LEDS))

def get_right_quarter():
    """LEDs für rechtes Viertel (oben rechts) - die beim Rechts-Schauen ausgehen"""
    # Bei 12 LEDs: 1, 2, 3 (3 LEDs) - LED 0 bleibt immer an
    quarter = NUM_LEDS // 4
    return list(range(1, quarter + 1))

def get_lower_left_quarter():
    """LEDs für unten links - die beim Rechts-Schauen angehen"""
    # Bei 12 LEDs: 6, 7, 8 (3 LEDs)
    quarter = NUM_LEDS // 4
    half = NUM_LEDS // 2
    return list(range(half, half + quarter))

def get_lower_right_quarter():
    """LEDs für unten rechts - die beim Links-Schauen angehen"""
    # Bei 12 LEDs: 4, 5, 6 (3 LEDs)
    # Obere Hälfte endet bei LED 3, also starten wir bei LED 4
    quarter = NUM_LEDS // 4
    half = NUM_LEDS // 2
    # Von LED quarter+1 bis half (inklusiv)
    return list(range(quarter + 1, half + 1))

def look_straight():
    """Auge schaut geradeaus (obere Hälfte an)"""
    clear_all()
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)

    for led in get_upper_half():
        np[led] = color
    np.write()

def blink():
    """Blinzel-Animation: Nur obere LEDs gehen aus (ganzer Ring wird dunkel)"""
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)
    upper = get_upper_half()

    # Phase 1: Auge schließt sich - alle oberen LEDs von außen nach innen ausschalten
    steps = (len(upper) + 1) // 2  # Aufrunden, um alle LEDs zu erfassen

    for step in range(steps):
        # Von beiden Seiten gleichzeitig ausschalten
        if step < len(upper):
            left_idx = upper[step]
            np[left_idx] = OFF

        # Von rechts (rückwärts durch die Liste)
        right_step = len(upper) - 1 - step
        if right_step >= 0 and right_step != step:  # Nicht dieselbe LED zweimal
            right_idx = upper[right_step]
            np[right_idx] = OFF

        np.write()
        sleep(0.05)

    # Kurz komplett geschlossen halten (alle LEDs aus)
    clear_all()
    sleep(0.15)

    # Phase 2: Auge öffnet sich wieder - obere LEDs von innen nach außen anschalten
    for step in range(steps):
        # Von der Mitte nach außen
        mid = len(upper) // 2

        # Linke Seite von der Mitte nach außen
        left_step = mid - step
        if left_step >= 0 and left_step < len(upper):
            np[upper[left_step]] = color

        # Rechte Seite von der Mitte nach außen
        right_step = mid + step
        if right_step < len(upper) and right_step != left_step:
            np[upper[right_step]] = color

        np.write()
        sleep(0.05)

    # Zurück zur normalen Position
    look_straight()

def look_left():
    """Auge schaut nach links (schrittweise Transition)"""
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)

    left_upper = get_left_quarter()
    lower_right = get_lower_right_quarter()

    steps = max(len(left_upper), len(lower_right))

    # Hinweg: Linke obere LEDs aus, rechte untere LEDs an (im Uhrzeigersinn)
    for step in range(steps):
        if step < len(left_upper):
            np[left_upper[step]] = OFF

        if step < len(lower_right):
            np[lower_right[step]] = color

        np.write()
        sleep(0.08)

    sleep(0.5)  # Kurz nach links schauen

    # Rückweg: In umgekehrter Reihenfolge (gegen Uhrzeigersinn zurückrollen)
    for step in range(steps - 1, -1, -1):
        if step < len(lower_right):
            np[lower_right[step]] = OFF

        if step < len(left_upper):
            np[left_upper[step]] = color

        np.write()
        sleep(0.08)

def look_right():
    """Auge schaut nach rechts (schrittweise Transition)"""
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)

    right_upper = get_right_quarter()  # [1, 2, 3]
    lower_left = get_lower_left_quarter()  # [6, 7, 8]

    steps = max(len(right_upper), len(lower_left))

    # Hinweg: Rechte obere LEDs aus, linke untere LEDs an (gegen Uhrzeigersinn)
    # LEDs: 3 aus & 8 an, dann 2 aus & 7 an, dann 1 aus & 6 an
    for step in range(steps):
        # Rückwärts durch right_upper (3 -> 2 -> 1)
        if step < len(right_upper):
            idx = len(right_upper) - 1 - step
            np[right_upper[idx]] = OFF

        # Rückwärts durch lower_left (8 -> 7 -> 6)
        if step < len(lower_left):
            idx = len(lower_left) - 1 - step
            np[lower_left[idx]] = color

        np.write()
        sleep(0.08)

    sleep(0.5)  # Kurz nach rechts schauen

    # Rückweg: Gespiegelt - im Uhrzeigersinn zurückrollen
    # LEDs: 6 aus & 1 an, dann 7 aus & 2 an, dann 8 aus & 3 an
    for step in range(steps - 1, -1, -1):
        # Vorwärts durch lower_left (6 -> 7 -> 8)
        if step < len(lower_left):
            idx = len(lower_left) - 1 - step
            np[lower_left[idx]] = OFF

        # Vorwärts durch right_upper (1 -> 2 -> 3)
        if step < len(right_upper):
            idx = len(right_upper) - 1 - step
            np[right_upper[idx]] = color

        np.write()
        sleep(0.08)

def eye_animation_cycle():
    """Ein kompletter Zyklus der Augen-Animation"""
    look_straight()
    sleep(1.5)
    blink()
    sleep(0.5)
    blink()
    sleep(0.5)
    look_left()
    sleep(0.3)
    look_right()
    sleep(0.3)

# Hauptprogramm (nur wenn direkt ausgeführt)
if __name__ == "__main__":
    print("\n" + "="*40)
    print("  NEOPIXEL AUGEN-ANIMATION")
    print("="*40)
    print("NeoPixel: GP1 (2x {} LEDs parallel)".format(NUM_LEDS))
    print("Sequenz: Geradeaus -> Blinzeln ->")
    print("         Links -> Rechts -> Loop")
    print("Drücke Strg+C zum Beenden")
    print("="*40 + "\n")

    try:
        # Initialisierung
        clear_all()
        sleep(0.5)

        while True:
            print("Animation...")
            eye_animation_cycle()

    except KeyboardInterrupt:
        clear_all()
        print("\n\nBeendet!")
