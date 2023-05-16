import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

prefix = "MYNAME/"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SSID', 'PWD')
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)


def callback(topic, msg):
    t = topic.decode("utf-8").lstrip(prefix)
    print(t)
    if t[:5] == 'GPIO/':
        p = int(t[5:])
        data = int(msg)
        led = Pin(p, Pin.OUT)
        led.value(data)
        client.publish(prefix+'DEVICE_NAME', str(p)+"-"+str(data))

def heartbeat(first):
    global lastping
    if first:
        client.ping()
        lastping = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), lastping) >= 300000:
        client.ping()
        lastping = time.ticks_ms()
    return

client = MQTTClient(prefix+"DEVICE_NAME", "IP_ADD", port=0000, user="USER_NAME", password="USER_PWD", keepalive=300, ssl=False, ssl_params={})
client.connect()
heartbeat(True)
client.set_callback(callback)
client.subscribe(prefix+"GPIO/#")
while True:
    client.check_msg()
    heartbeat(False)

