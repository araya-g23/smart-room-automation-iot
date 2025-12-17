import time
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temp: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
    except RuntimeError as e:
        print("Error reading DHT22:", e)
    time.sleep(2)
