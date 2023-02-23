from machine import Pin

led = machine.Pin("LED", Pin.OUT)

led.toggle()

if led.value() == 1:
    print("LED is ON")
else:
    print ("LED is OFF")    

print (led)