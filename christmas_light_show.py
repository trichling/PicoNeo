from machine import Pin, PWM
from neopixel import NeoPixel
from time import sleep

# Verfügbare Melodien importieren
import melody_jingle_bells
import melody_we_wish_you

# Hardware-Konfiguration
NUM_LEDS = 12  # Anzahl LEDs im Ring anpassen!
neopixel_pin = Pin(1, Pin.OUT)  # GP1 für NeoPixel
np = NeoPixel(neopixel_pin, NUM_LEDS)

buzzer = PWM(Pin(19))  # GP19 für Buzzer

# Lautstärke-Einstellungen
VOLUME_LOW = 16384      # 25% Duty Cycle
VOLUME_MEDIUM = 32768   # 50% Duty Cycle
VOLUME_HIGH = 49152     # 75% Duty Cycle
VOLUME_MAX = 65535      # 100% Duty Cycle
VOLUME = VOLUME_MEDIUM

# Notendefinitionen (Frequenzen in Hz)
NOTES = {
    'C4': 262,
    'D4': 294,
    'E4': 330,
    'F4': 349,
    'G4': 392,
    'A4': 440,
    'B4': 494,
    'C5': 523,
    'D5': 587,
    'E5': 659,
    'F5': 698,
    'G5': 784,
    'REST': 0
}

# Frequenzbereich für Helligkeit-Mapping
MIN_FREQ = 262  # C4
MAX_FREQ = 784  # G5

# Melodie-Auswahl
MELODIES = {
    1: ("Jingle Bells", melody_jingle_bells.melody),
    2: ("We Wish You a Merry Christmas", melody_we_wish_you.melody),
}

# Globale Variablen für weiche Übergänge
current_brightness = 0
current_hue = 0

def hsv_to_rgb(h, s, v):
    """Konvertiert HSV zu RGB (h: 0-360, s: 0-1, v: 0-1)"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

def freq_to_brightness(frequency):
    """Mappt Frequenz auf Helligkeit (0.1 bis 1.0) mit stärkerer Spreizung"""
    if frequency == 0:
        return 0.0

    # Normalisiere Frequenz zwischen MIN_FREQ und MAX_FREQ
    normalized = (frequency - MIN_FREQ) / (MAX_FREQ - MIN_FREQ)
    normalized = max(0.0, min(1.0, normalized))  # Clamp auf 0-1

    # Exponentialfunktion für stärkere Kontraste
    # Niedrige Töne werden dunkler, hohe Töne heller
    normalized = normalized ** 2  # Quadratische Funktion verstärkt Unterschiede

    # Skaliere auf Helligkeitsbereich 0.1-1.0 (mindestens 10% Helligkeit)
    return 0.1 + (normalized * 0.9)

def smooth_transition(current, target, speed=0.05):
    """Weicher Übergang zwischen Werten"""
    diff = target - current
    return current + (diff * speed)

def fade_to_black(fade_duration):
    """Dimmt die LEDs sanft auf schwarz herunter

    Args:
        fade_duration: Gesamtdauer des Fade-Effekts in Sekunden
    """
    global current_brightness

    # Mehr Schritte für weicheres Fading
    steps = max(5, int(fade_duration * 100))  # 100 Updates pro Sekunde für sehr weiches Fading
    step_duration = fade_duration / steps

    for _ in range(steps):
        # Exponentielles Abdimmen (schnell am Anfang, langsamer am Ende)
        current_brightness = current_brightness * 0.85

        # Stoppe bei sehr niedriger Helligkeit
        if current_brightness < 0.01:
            current_brightness = 0.0
            break

        r = int(255 * current_brightness)
        for i in range(NUM_LEDS):
            np[i] = (r, 0, 0)
        np.write()
        sleep(step_duration)

def update_neopixel(frequency, duration):
    """Aktualisiert NeoPixel mit weichen Übergängen"""
    global current_brightness

    # Ziel-Helligkeit basierend auf Frequenz
    target_brightness = freq_to_brightness(frequency)

    # Anzahl der Update-Schritte für weiche Übergänge
    steps = max(5, int(duration * 50))  # 50 Updates pro Sekunde
    step_duration = duration / steps

    for step in range(steps):
        # Weicher Helligkeits-Übergang
        current_brightness = smooth_transition(current_brightness, target_brightness, 0.3)

        # Feste rote Farbe mit variabler Helligkeit
        r = int(255 * current_brightness)
        g = 0
        b = 0

        # Alle LEDs auf die gleiche Farbe setzen
        for i in range(NUM_LEDS):
            np[i] = (r, g, b)
        np.write()

        sleep(step_duration)

def play_tone(frequency, duration):
    """Spielt einen Ton mit gegebener Frequenz und Dauer"""
    if frequency == 0:
        buzzer.duty_u16(0)  # Pause
    else:
        buzzer.freq(frequency)
        buzzer.duty_u16(VOLUME)

    # NeoPixel parallel aktualisieren
    update_neopixel(frequency, duration)

    buzzer.duty_u16(0)  # Ton aus

    # Schnelles Abdimmen zwischen Tönen für stärkeren Pulsierungseffekt
    fade_to_black(0.05)  # 50ms Fade-Pause zwischen Noten

def play_melody(melody):
    """Spielt eine komplette Melodie"""
    for note, duration in melody:
        frequency = NOTES[note]
        play_tone(frequency, duration)

def clear_neopixel():
    """Schaltet alle NeoPixel aus"""
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# Hauptprogramm
print("\n" + "="*40)
print("  WEIHNACHTS-LICHT-SHOW")
print("="*40)
print("NeoPixel: GP1 ({} LEDs)".format(NUM_LEDS))
print("Buzzer: GP15")
print("Helligkeit ~ Tonhöhe")
print("Farbe: Rot")
print("Drücke Strg+C zum Beenden")
print("="*40 + "\n")

try:
    while True:
        for num, (name, melody) in MELODIES.items():
            print(f"Spiele: {name}")
            play_melody(melody)

            # Sanftes Ausblenden am Ende
            for _ in range(10):
                current_brightness = smooth_transition(current_brightness, 0, 0.2)
                r = int(255 * current_brightness)
                for i in range(NUM_LEDS):
                    np[i] = (r, 0, 0)
                np.write()
                sleep(0.1)

            clear_neopixel()
            sleep(2)  # Pause zwischen verschiedenen Liedern

except KeyboardInterrupt:
    buzzer.duty_u16(0)
    buzzer.deinit()
    clear_neopixel()
    print("\n\nBeendet - Frohe Weihnachten!")
