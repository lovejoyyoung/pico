import time
import socket
import network
from machine import Pin
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

#initialize LED
led = machine.Pin("LED", Pin.OUT)
ledState = 'LED State Unknown'

#network connection
ssid = ''
password = ''
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# set up the hardware
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=0)
sensor_temp = machine.ADC(4)
ledscreen = RGBLED(6, 7, 8)

# set the display backlight to 50%
display.set_backlight(0.7)

# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)

# used for calculating a temperature from the raw sensor reading
conversion_factor = 3.3 / (65535)
temp_min = 10
temp_max = 30
bar_width = 5
temperatures = []
colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]

#HTML PAGE DESIGN
html = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" http-equiv="refresh" content="5">
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
    <center><h1>PicoW X PicoDisplay</h1></center>
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
  print('ip = ' + status[0])

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('listening on', addr)

# Define temp to color
def temperature_to_color(temp):
    temp = min(temp, temp_max)
    temp = max(temp, temp_min)

    f_index = float(temp - temp_min) / float(temp_max - temp_min)
    f_index *= len(colors) - 1
    index = int(f_index)

    if index == len(colors) - 1:
        return colors[index]

    blend_b = f_index - index
    blend_a = 1.0 - blend_b

    a = colors[index]
    b = colors[index + 1]

    return [int((a[i] * blend_a) + (b[i] * blend_b)) for i in range(3)]


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
    print('led on = ' + str(led_on))
    print('led off = ' + str(led_off))
    if led_on == 8:
      print("led on")
      led.value(1)
    if led_off == 8:
      print("led off")
      led.value(0)
      
    # fills the screen with black
    display.set_pen(BLACK)
    display.clear()

    # the following two lines do some maths to convert the number from the temp sensor into celsius
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706) / 0.001721
    temperatures.append(temperature)
    tempOnline = '\n Temperature: %0.2f C' % temperature
    
    
    
    # shifts the temperatures history to the left by one sample
    if len(temperatures) > WIDTH // bar_width:
        temperatures.pop(0)

    i = 0

    for t in temperatures:
        # chooses a pen colour based on the temperature
        TEMPERATURE_COLOUR = display.create_pen(*temperature_to_color(t))
        display.set_pen(TEMPERATURE_COLOUR)

        # draws the reading as a tall, thin rectangle
        display.rectangle(i, HEIGHT - (round(t) * 3), bar_width, HEIGHT)

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width

    # heck lets also set the LED to match
    ledscreen.set_rgb(*temperature_to_color(temperature))

    # draws a white background for the text
    display.set_pen(WHITE)
    display.rectangle(1, 1, 100, 25)

    # writes the reading as text in the white rectangle
    display.set_pen(BLACK)
    display.text("{:.2f}".format(temperature) + "°C", 3, 3, 0, 3)
    
    #The display of state in HTML below the buttons
    ledState = "LED State is OFF" if led.value() == 0 else "LED State is ON"

    # time to update the display
    display.update()

    # waits for 5 seconds
    time.sleep(5)
    
    #Create response then send data
    response = html % tempOnline + ledState
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()

  except OSError as e:
    cl.close()
    print('connection closed')
