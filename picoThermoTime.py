import time
import utime
from machine import Pin
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

#initialize LED ON
led = machine.Pin("LED", Pin.OUT)

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
temp_max = 40
bar_width = 3
temperatures = []
colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]

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
    # fills the screen with black
    display.set_pen(BLACK)
    display.clear()

    # the following two lines do some maths to convert the number from the temp sensor into celsius
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706) / 0.001721
    temperatures.append(temperature)

    # shifts the temperatures history to the left by one sample
    if len(temperatures) > WIDTH // bar_width:
        temperatures.pop(0)

    i = 0

    for t in temperatures:
        # chooses a pen colour based on the temperature
        TEMPERATURE_COLOUR = display.create_pen(*temperature_to_color(t))
        display.set_pen(TEMPERATURE_COLOUR)

        # draws the reading as a tall, thin rectangle
        display.rectangle(i, HEIGHT - (round(t) * 2), bar_width, HEIGHT)

        # the next tall thin rectangle needs to be drawn
        # "bar_width" (default: 5) pixels to the right of the last one
        i += bar_width

    # heck lets also set the LED to match
    ledscreen.set_rgb(*temperature_to_color(temperature))

    #Get current time
    current_time = utime.localtime()

    #Format time as HH:MM:SS
    time_str = "{:02d}:{:02d}:{:02d}".format(
        current_time[3], current_time[4], current_time[5])

    # draws a white background for the text
    display.set_pen(WHITE)
    display.rectangle(1, 1, 110, 25)

    # draws a white background for the 2nd text
    display.set_pen(WHITE)
    display.rectangle(130, 1, 255, 25)

    # writes the reading as text in the white rectangle
    display.set_pen(BLACK)
    display.text("{:.2f}".format(temperature) + "°C", 6, 3, 0, 3)

    # writes the reading as 2nd text in the white rectangle
    display.set_pen(BLACK)
    display.text(time_str, 135, 3, 0, 3)

    # time to update the display
    display.update()

    # waits for 5 seconds
    time.sleep(1)
