from machine import Pin
from neopixel import NeoPixel
from time import sleep

# NeoPixel Ring konfigurieren
# GP1 als Datenleitung, Anzahl der LEDs im Ring anpassen (meist 8, 12, 16, 24 oder 60)
NUM_LEDS = 12  # Ändere dies auf die Anzahl LEDs in deinem Ring
pin = Pin(1, Pin.OUT)  # GP1
np = NeoPixel(pin, NUM_LEDS)

print(f"NeoPixel Ring mit {NUM_LEDS} LEDs auf GP1 initialisiert")

# Alle LEDs ausschalten
def clear():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# Test 1: Alle LEDs rot
print("Test 1: Alle LEDs rot")
for i in range(NUM_LEDS):
    np[i] = (255, 0, 0)  # (R, G, B)
np.write()
sleep(2)

# Test 2: Alle LEDs grün
print("Test 2: Alle LEDs grün")
for i in range(NUM_LEDS):
    np[i] = (0, 255, 0)
np.write()
sleep(2)

# Test 3: Alle LEDs blau
print("Test 3: Alle LEDs blau")
for i in range(NUM_LEDS):
    np[i] = (0, 0, 255)
np.write()
sleep(2)

# Test 4: Lauflicht
print("Test 4: Lauflicht (Strg+C zum Beenden)")
try:
    while True:
        for i in range(NUM_LEDS):
            clear()
            # Aktuelles LED in Regenbogenfarbe
            hue = int((i / NUM_LEDS) * 255)
            if hue < 85:
                r, g, b = 255 - hue * 3, hue * 3, 0
            elif hue < 170:
                hue -= 85
                r, g, b = 0, 255 - hue * 3, hue * 3
            else:
                hue -= 170
                r, g, b = hue * 3, 0, 255 - hue * 3

            np[i] = (r, g, b)
            np.write()
            sleep(0.1)
except KeyboardInterrupt:
    print("\nBeendet")
    clear()
    print("Alle LEDs ausgeschaltet")
