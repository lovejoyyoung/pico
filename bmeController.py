# Simple HTTP Server Example
# Control an LED and read a Button using a web browser
# BME280 SENSOR MONTIOR ASSEMBLE
import network
import socket
import busio
import board
import time
from time import sleep
from machine import Pin, I2C, Timer
from adafruit_bme280 import basic as adafruit_bme280
from dotenv import load_dotenv
import os

load_dotenv()

#initialize LED
led = machine.Pin("LED", Pin.OUT)
ledState = 'LED State Unknown'

#initialize I2C
i2c = busio.I2C(board.GP1, board.GP0)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#network connection
ssid = os.getenv('NETWORK_SSID')
password = os.getenv('NETWORK_PWD')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#HTML PAGE DESIGN
html = """
<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" http-equiv="refresh" content="30">
        <link rel="icon" href="https://www.raspberrypi.com/favicon.ico">
        <style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center; background-color:lightgrey}
               .buttonGreen { background-color: #4CAF50; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
               .buttonRed { background-color: #D11D53; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
               text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
        </style>
    </head>
    <body>
        <center><h1>LED Wifi Control Panel</h1></center>
        <br><br>
        <form>
            <center>
            <button class="buttonGreen" name="led" value="on" type="submit">LED ON</button>
            <br><br>
            <center>
            <button class="buttonRed" name="led" value="off" type="submit">LED OFF</button>   
        </form>
        <br><br>
        <br><br>
        <center><h1>Pico W Weather Station & LED State</h1></center>
        <br><br>
        <h2>%s<h2>
        <br><br>
        
    </body>
</html>
"""

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)
    
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('listening on', addr)

# Listen for connections, serve client
while True:
    try:       
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print("request:")
        print(request)
        request = str(request)
        
        #Storage url value 
        led_on = request.find('led=on')
        led_off = request.find('led=off')
        
        #The display of state in Shell consoles
        print( 'led on = ' + str(led_on))
        print( 'led off = ' + str(led_off))
        
        if led_on == 8:
            print("led on")
            led.value(1)
        if led_off == 8:
            print("led off")
            led.value(0)
            
        #Creat value of bme280 and varitey measure value
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        temp = bme280.temperature
        humidity = bme280.relative_humidity
        pressure = bme280.pressure
        reading = '\n Temperature: %0.1f C' % temp +'<br><br> Humidity: %0.1f %%'% humidity + '<br><br> Pressure: %0.1f hPa' % bme280.pressure
        
        #The display of state in HTML below the buttons  
        ledState = "LED State is OFF" if led.value() == 0 else "LED State is ON"           

        #Create response then send data
        response = html % reading + ledState
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        
    except OSError as e:
        cl.close()
        print('connection closed')

