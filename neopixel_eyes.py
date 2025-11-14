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

# Callback-Funktion für Interrupt-Checks (wird von main.py gesetzt)
interrupt_check = None  # type: ignore

def scale_color(color, brightness):
    """Skaliert eine Farbe mit Helligkeitsfaktor"""
    return tuple(int(c * brightness) for c in color)

def interruptible_sleep(duration):
    """Sleep-Funktion die durch Button-Callback unterbrochen werden kann

    Args:
        duration: Schlafdauer in Sekunden

    Returns:
        True wenn unterbrochen wurde, False wenn die Zeit normal abgelaufen ist
    """
    if interrupt_check is None:
        # Kein Interrupt-Check gesetzt, normales Sleep
        sleep(duration)
        return False

    # Teile die Wartezeit in kleine Intervalle auf (50ms)
    interval = 0.05
    elapsed = 0.0

    while elapsed < duration:
        # Prüfe ob unterbrochen werden soll
        if interrupt_check():
            return True

        # Schlafe für ein kleines Intervall
        sleep(interval)
        elapsed += interval

    return False

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
    """Auge schaut nach links (9 o'clock Richtung)

    Returns:
        True wenn durch Button unterbrochen, False sonst
    """
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)

    # Hinweg: Von 12-6 o'clock Position nach links rollen
    # Schritt 1: LED 9 (3 o'clock) aus
    np[9] = OFF  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 2: LED 8 aus, LED 2 an (swap)
    np[8] = OFF  # type: ignore
    np[2] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 3: LED 7 aus, LED 1 an (swap)
    np[7] = OFF  # type: ignore
    np[1] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 4: LED 0 (6 o'clock) an
    np[0] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # In der Endposition verweilen (1-3 Sekunden, interruptible)
    if interruptible_sleep(random.uniform(1.0, 3.0)):
        return True

    # Rückweg: Zurück zur Ausgangsposition (umgekehrt)
    # Schritt 4 rückwärts: LED 0 aus
    np[0] = OFF  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 3 rückwärts: LED 1 aus, LED 7 an
    np[1] = OFF  # type: ignore
    np[7] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 2 rückwärts: LED 2 aus, LED 8 an
    np[2] = OFF  # type: ignore
    np[8] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 1 rückwärts: LED 9 an
    np[9] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    return False

def look_right():
    """Auge schaut nach rechts (3 o'clock Richtung)

    Returns:
        True wenn durch Button unterbrochen, False sonst
    """
    color = scale_color(EYE_COLOR, EYE_BRIGHTNESS)

    # Hinweg: Von 12-6 o'clock Position nach rechts rollen
    # Schritt 1: LED 3 (9 o'clock) aus
    np[3] = OFF  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 2: LED 4 aus, LED 10 an (swap)
    np[4] = OFF  # type: ignore
    np[10] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 3: LED 5 aus, LED 11 an (swap)
    np[5] = OFF  # type: ignore
    np[11] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 4: LED 0 (6 o'clock) an
    np[0] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # In der Endposition verweilen (1-3 Sekunden, interruptible)
    if interruptible_sleep(random.uniform(1.0, 3.0)):
        return True

    # Rückweg: Zurück zur Ausgangsposition (umgekehrt)
    # Schritt 4 rückwärts: LED 0 aus
    np[0] = OFF  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 3 rückwärts: LED 11 aus, LED 5 an
    np[11] = OFF  # type: ignore
    np[5] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 2 rückwärts: LED 10 aus, LED 4 an
    np[10] = OFF  # type: ignore
    np[4] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    # Schritt 1 rückwärts: LED 3 an
    np[3] = color  # type: ignore
    np.write()  # type: ignore
    sleep(0.08)

    return False

def do_animation():
    """Führt eine zufällige Augen-Animation aus und kehrt danach zurück

    Diese Funktion wird von main.py in einer Schleife aufgerufen.
    Sie wählt zufällig eine Animation basierend auf Wahrscheinlichkeiten
    und führt diese komplett aus, bevor sie zurückkehrt.

    Returns:
        True wenn durch Button unterbrochen, False sonst
    """
    # Sicherstellen dass Auge gerade schaut
    look_straight()

    # Bestimme zufällige Aktion mit gewichteter Wahrscheinlichkeit
    action = random.randint(1, 100)

    if action <= 60:
        # 60% Chance: Nur blinzeln (häufigste Aktion)
        blink()
        if interruptible_sleep(random.uniform(0.3, 1.0)):
            return True

        # Manchmal doppelt blinzeln
        if random.randint(1, 100) <= 30:  # 30% Chance
            if interruptible_sleep(random.uniform(0.2, 0.5)):
                return True
            blink()

    elif action <= 85:
        # 25% Chance: Blinzeln, dann in eine Richtung schauen
        blink()
        if interruptible_sleep(random.uniform(0.3, 0.6)):
            return True

        if random.randint(1, 2) == 1:
            if look_left():
                return True
        else:
            if look_right():
                return True

    elif action <= 95:
        # 10% Chance: Nur in eine Richtung schauen (ohne Blinzeln)
        if random.randint(1, 2) == 1:
            if look_left():
                return True
        else:
            if look_right():
                return True

    else:
        # 5% Chance: Links und rechts schauen (ohne Blinzeln dazwischen)
        if random.randint(1, 2) == 1:
            if look_left():
                return True
            if interruptible_sleep(random.uniform(0.2, 0.4)):
                return True
            if look_right():
                return True
        else:
            if look_right():
                return True
            if interruptible_sleep(random.uniform(0.2, 0.4)):
                return True
            if look_left():
                return True

    return False

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
            do_animation()

    except KeyboardInterrupt:
        clear_all()
        print("\n\nBeendet!")
