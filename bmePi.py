import time
import threading
import board
from gpiozero import CPUTemperature
from flask import Flask
from adafruit_bme280 import basic as adafruit_bme280

# Create sensor object, using the board's default I2C bus.
i2c = board.I2C()

# uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1023.1


html = """
<!DOCTYPE html>
<meta http-equiv="refresh" content="5" >
<html>
    <head> 
        <title>RPI_BME280</title> 
        <link rel="icon" href="https://www.raspberrypi.com/favicon.ico">
    </head>
    <body style="text-align: center; background-color: lightgrey; font-size: 50px">
        <h1>RPi X BME280 Sensor</h1>
        <h2>{cpu}</h2>
        <h2>{temp}</h2>
        <h2>{humi}</h2>
        <h2>{pre}</h2>
        <h2>{alt}</h2>
    </body>
</html>
"""

app = Flask(__name__)


@app.route('/')
def index():

    cpu = CPUTemperature()
    c = "\nCPU Temp: %0.1f C" % cpu.temperature
    t = "Temperature: %0.1f C" % bme280.temperature
    h = "Humidity: %0.1f %%" % bme280.relative_humidity
    p = "Pressure: %0.1f hPa" % bme280.pressure
    a = "Altitude: %0.2f meters" % bme280.altitude

    response = html.format(cpu=c, temp=t, humi=h, pre=p, alt=a)
    return response, {'Content-Type': 'text/html'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
