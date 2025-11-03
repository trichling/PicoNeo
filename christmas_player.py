from machine import Pin, PWM
from time import sleep

# Verfügbare Melodien importieren
import melody_jingle_bells
import melody_we_wish_you

# Lautstärke-Einstellungen
VOLUME_LOW = 16384      # 25% Duty Cycle
VOLUME_MEDIUM = 32768   # 50% Duty Cycle
VOLUME_HIGH = 49152     # 75% Duty Cycle
VOLUME_MAX = 65535      # 100% Duty Cycle

# Aktuelle Lautstärke
VOLUME = VOLUME_MEDIUM

# Passiver Buzzer an GP15
buzzer = PWM(Pin(15))

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

# Melodie-Auswahl
MELODIES = {
    1: ("Jingle Bells", melody_jingle_bells.melody),
    2: ("We Wish You a Merry Christmas", melody_we_wish_you.melody),
}

def play_tone(frequency, duration):
    """Spielt einen Ton mit gegebener Frequenz und Dauer"""
    if frequency == 0:
        buzzer.duty_u16(0)  # Pause
    else:
        buzzer.freq(frequency)
        buzzer.duty_u16(VOLUME)
    sleep(duration)
    buzzer.duty_u16(0)  # Ton aus
    sleep(0.05)  # Kurze Pause zwischen Noten

def play_melody(melody):
    """Spielt eine komplette Melodie"""
    for note, duration in melody:
        frequency = NOTES[note]
        play_tone(frequency, duration)

# Hauptprogramm
print("\n" + "="*40)
print("  WEIHNACHTS-MELODIEN PLAYER")
print("="*40)
print("Buzzer an GP15")
print("Spiele alle Melodien nacheinander...")
print("Drücke Strg+C zum Beenden")
print("="*40 + "\n")

try:
    while True:
        for num, (name, melody) in MELODIES.items():
            print(f"Spiele: {name}")
            play_melody(melody)
            sleep(3)  # Pause zwischen verschiedenen Liedern

except KeyboardInterrupt:
    buzzer.duty_u16(0)
    buzzer.deinit()
    print("\n\nBeendet - Frohe Weihnachten!")
