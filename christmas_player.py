from machine import Pin, PWM
from time import sleep

# Verfügbare Melodien importieren
import melody_jingle_bells
import melody_we_wish_you
import melody_silent_night

# Lautstärke-Einstellungen
VOLUME_LOW = 16384      # 25% Duty Cycle
VOLUME_MEDIUM = 32768   # 50% Duty Cycle
VOLUME_HIGH = 49152     # 75% Duty Cycle
VOLUME_MAX = 65535      # 100% Duty Cycle

# Aktuelle Lautstärke
VOLUME = VOLUME_MEDIUM

# Passiver Buzzer an GP8
buzzer = PWM(Pin(8))

# Notendefinitionen (Frequenzen in Hz)
NOTES = {
    'C4': 262,
    'C#4': 277,
    'D4': 294,
    'E4': 330,
    'F4': 349,
    'F#4': 370,
    'G4': 392,
    'G#4': 415,
    'A4': 440,
    'B4': 494,
    'C5': 523,
    'C#5': 554,
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
    3: ("Silent Night", melody_silent_night.melody),
}

# ==========================================
# TEST-KONFIGURATION
# ==========================================
# Wähle ein Lied zum Testen (None = alle Lieder nacheinander)
# Optionen: None, 1, 2, 3
#   1 = "Jingle Bells"
#   2 = "We Wish You a Merry Christmas"
#   3 = "Silent Night"
TEST_SONG = 3  # Ändere auf 1, 2 oder 3 um nur ein Lied zu testen
# ==========================================

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
if TEST_SONG is not None:
    print(f"TEST-MODUS: Nur Lied #{TEST_SONG}")
else:
    print("Spiele alle Melodien nacheinander...")
print("Drücke Strg+C zum Beenden")
print("="*40 + "\n")

try:
    while True:
        # Wähle Lieder basierend auf TEST_SONG Konfiguration
        if TEST_SONG is not None:
            # Nur ein bestimmtes Lied testen
            songs_to_play = [(TEST_SONG, MELODIES[TEST_SONG])]
        else:
            # Alle Lieder nacheinander
            songs_to_play = MELODIES.items()

        for num, (name, melody) in songs_to_play:
            print(f"Spiele: {name}")
            play_melody(melody)
            sleep(3)  # Pause zwischen verschiedenen Liedern

except KeyboardInterrupt:
    buzzer.duty_u16(0)
    buzzer.deinit()
    print("\n\nBeendet - Frohe Weihnachten!")
