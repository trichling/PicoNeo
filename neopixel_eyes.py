from machine import Pin
from neopixel import NeoPixel
from time import sleep
import random

# Hardware-Konfiguration
NUM_LEDS = 12  # Anzahl LEDs pro Ring (beide Ringe parallel geschaltet)
np = None  # type: ignore  # Wird von main.py oder beim direkten Start initialisiert

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
        np[i] = OFF  # type: ignore
    np.write()  # type: ignore

def get_upper_half():
    """Gibt die LED-Indizes für die obere Hälfte zurück (Auge offen)"""
    # Bei 12 LEDs und 180° Drehung: LED 6 ist oben, dann im Uhrzeigersinn
    # Obere Hälfte: LEDs 3, 4, 5, 6, 7, 8, 9
    quarter = NUM_LEDS // 4
    half = NUM_LEDS // 2

    # Von links-oben über oben nach rechts-oben (180° gedreht)
    upper = []
    for i in range(NUM_LEDS):
        # Obere Hälfte: von quarter bis three_quarter (bei 12 LEDs: 3 bis 9)
        if i >= quarter and i <= half + quarter:
            upper.append(i)
    return upper

def get_lower_half():
    """Gibt die LED-Indizes für die untere Hälfte zurück"""
    # 180° gedreht: Untere Hälfte: LEDs 10, 11, 0, 1, 2
    quarter = NUM_LEDS // 4
    three_quarter = NUM_LEDS * 3 // 4

    lower = []
    for i in range(NUM_LEDS):
        # Untere Hälfte: von three_quarter bis quarter (wrap around)
        if i >= three_quarter or i < quarter:
            lower.append(i)
    return lower

def get_left_quarter():
    """LEDs für linkes Viertel (oben links) - die beim Links-Schauen ausgehen"""
    # 180° gedreht: Bei 12 LEDs: 3, 4, 5 (3 LEDs)
    quarter = NUM_LEDS // 4
    return list(range(quarter, quarter * 2))

def get_right_quarter():
    """LEDs für rechtes Viertel (oben rechts) - die beim Rechts-Schauen ausgehen"""
    # 180° gedreht: Bei 12 LEDs: 7, 8, 9 (3 LEDs) - LED 6 bleibt immer an
    quarter = NUM_LEDS // 4
    half = NUM_LEDS // 2
    return list(range(half + 1, half + quarter + 1))

def get_lower_left_quarter():
    """LEDs für unten links - die beim Rechts-Schauen angehen"""
    # 180° gedreht: Bei 12 LEDs: 0, 1, 2 (3 LEDs)
    quarter = NUM_LEDS // 4
    return list(range(0, quarter))

def get_lower_right_quarter():
    """LEDs für unten rechts - die beim Links-Schauen angehen"""
    # 180° gedreht: Bei 12 LEDs: 10, 11 (nur 2 LEDs wegen wrap-around)
    three_quarter = NUM_LEDS * 3 // 4
    # Wir geben die letzten LEDs zurück: 10, 11
    return list(range(three_quarter, NUM_LEDS))

def look_straight():
    """Auge schaut geradeaus (obere Hälfte an)"""
    clear_all()
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)

    for led in get_upper_half():
        np[led] = color  # type: ignore
    np.write()  # type: ignore

def blink():
    """Blinzel-Animation: LEDs gehen von der Mitte nach außen aus (Augenlid schließt sich)"""
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)
    upper = get_upper_half()  # [3, 4, 5, 6, 7, 8, 9]

    # Phase 1: Auge schließt sich - von der Mitte (LED 6) nach außen
    # Mitte finden
    mid = len(upper) // 2  # Index 3 in der Liste -> LED 6

    # Von der Mitte nach außen ausschalten
    for step in range(mid + 1):
        # Mittlere LED zuerst, dann symmetrisch nach außen
        # step 0: LED 6 (Mitte)
        # step 1: LED 5 und 7
        # step 2: LED 4 und 8
        # step 3: LED 3 und 9

        # Mitte ausschalten
        if step == 0:
            np[upper[mid]] = OFF  # type: ignore
        else:
            # Links von der Mitte
            left_idx = mid - step
            if left_idx >= 0:
                np[upper[left_idx]] = OFF  # type: ignore

            # Rechts von der Mitte
            right_idx = mid + step
            if right_idx < len(upper):
                np[upper[right_idx]] = OFF  # type: ignore

        np.write()  # type: ignore
        sleep(0.05)

    # Kurz komplett geschlossen halten (alle LEDs aus)
    clear_all()
    sleep(0.15)

    # Phase 2: Auge öffnet sich wieder - von außen nach innen
    # In umgekehrter Reihenfolge
    for step in range(mid, -1, -1):
        if step == 0:
            # Mitte anschalten
            np[upper[mid]] = color  # type: ignore
        else:
            # Äußere LEDs zuerst, dann nach innen
            left_idx = mid - step
            if left_idx >= 0:
                np[upper[left_idx]] = color  # type: ignore

            right_idx = mid + step
            if right_idx < len(upper):
                np[upper[right_idx]] = color  # type: ignore

        np.write()  # type: ignore
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
            np[left_upper[step]] = OFF  # type: ignore

        if step < len(lower_right):
            np[lower_right[step]] = color  # type: ignore

        np.write()  # type: ignore
        sleep(0.08)

    sleep(0.5)  # Kurz nach links schauen

    # Rückweg: In umgekehrter Reihenfolge (gegen Uhrzeigersinn zurückrollen)
    for step in range(steps - 1, -1, -1):
        if step < len(lower_right):
            np[lower_right[step]] = OFF  # type: ignore

        if step < len(left_upper):
            np[left_upper[step]] = color  # type: ignore

        np.write()  # type: ignore
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
            np[right_upper[idx]] = OFF  # type: ignore

        # Rückwärts durch lower_left (8 -> 7 -> 6)
        if step < len(lower_left):
            idx = len(lower_left) - 1 - step
            np[lower_left[idx]] = color  # type: ignore

        np.write()  # type: ignore
        sleep(0.08)

    sleep(0.5)  # Kurz nach rechts schauen

    # Rückweg: Gespiegelt - im Uhrzeigersinn zurückrollen
    # LEDs: 6 aus & 1 an, dann 7 aus & 2 an, dann 8 aus & 3 an
    for step in range(steps - 1, -1, -1):
        # Vorwärts durch lower_left (6 -> 7 -> 8)
        if step < len(lower_left):
            idx = len(lower_left) - 1 - step
            np[lower_left[idx]] = OFF  # type: ignore

        # Vorwärts durch right_upper (1 -> 2 -> 3)
        if step < len(right_upper):
            idx = len(right_upper) - 1 - step
            np[right_upper[idx]] = color  # type: ignore

        np.write()  # type: ignore
        sleep(0.08)

def eye_animation_cycle():
    """Ein kompletter Zyklus der Augen-Animation mit natürlicher Zufälligkeit"""
    look_straight()
    sleep(random.uniform(1.0, 3.0))  # Zufällige Pause zwischen 1-3 Sekunden

    # Bestimme zufällige Aktion mit gewichteter Wahrscheinlichkeit
    action = random.randint(1, 100)

    if action <= 60:
        # 60% Chance: Nur blinzeln (häufigste Aktion)
        blink()
        sleep(random.uniform(0.3, 1.0))

        # Manchmal doppelt blinzeln
        if random.randint(1, 100) <= 30:  # 30% Chance
            sleep(random.uniform(0.2, 0.5))
            blink()

    elif action <= 85:
        # 25% Chance: Blinzeln, dann in eine Richtung schauen
        blink()
        sleep(random.uniform(0.3, 0.6))

        if random.randint(1, 2) == 1:
            look_left()
        else:
            look_right()

    elif action <= 95:
        # 10% Chance: Nur in eine Richtung schauen (ohne Blinzeln)
        if random.randint(1, 2) == 1:
            look_left()
        else:
            look_right()

    else:
        # 5% Chance: Links und rechts schauen (ohne Blinzeln dazwischen)
        if random.randint(1, 2) == 1:
            look_left()
            sleep(random.uniform(0.2, 0.4))
            look_right()
        else:
            look_right()
            sleep(random.uniform(0.2, 0.4))
            look_left()

    # Kurze Pause am Ende
    sleep(random.uniform(0.3, 0.8))

# Hauptprogramm (nur wenn direkt ausgeführt)
if __name__ == "__main__":
    # Hardware initialisieren wenn direkt ausgeführt
    neopixel_pin = Pin(1, Pin.OUT)
    np = NeoPixel(neopixel_pin, NUM_LEDS)

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
