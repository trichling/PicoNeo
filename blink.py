from machine import Pin
from time import sleep

# Für Pico W: Die LED muss speziell initialisiert werden
pin = Pin("LED", Pin.OUT)

print("LED starts flashing...")
while True:
    try:
        pin.on()
        print("LED ON")
        sleep(1)
        pin.off()
        print("LED OFF")
        sleep(1)
    except KeyboardInterrupt:
        break

pin.off()
print("Finished.")
