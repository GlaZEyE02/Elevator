try:
    import usocket as socket
except:
    import socket

import time
from machine import Pin, PWM
import network
import gc
gc.collect()


ssid = 'ITEK 1st'
password = 'itekf25v'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print("Connected:", station.ifconfig())


spinPin1 = Pin(0, Pin.OUT)
spinPin2 = Pin(1, Pin.OUT)
pwm1 = PWM(spinPin1)
pwm2 = PWM(spinPin2)
pwm1.freq(50)
pwm2.freq(50)

gy53 = Pin(28, Pin.IN)


web_command = None


state = "stable"


def measure_distance():
    while gy53.value() == 0:
        pass
    starttime = time.ticks_us()

    while gy53.value() == 1:
        pass
    endtime = time.ticks_us()

    pulse_width_us = time.ticks_diff(endtime, starttime)
    return pulse_width_us / 1000.0



def state_stable():
    global web_command

    pwm1.duty_u16(0)
    pwm2.duty_u16(0)

    if web_command:
        new_state = web_command
        web_command = None
        return new_state

    return "stable"


def state_stue(distance_mm):
    while not distance_mm < 0.5:
        distance_mm = measure_distance()
        pwm1.duty_u16(0)
        pwm2.duty_u16(32768)


    pwm1.duty_u16(0)
    pwm2.duty_u16(0)
    return "stable"

    return "stue"


def state_etage1(distance_mm):
    while not 1.5 <= distance_mm <= 1.7:
        distance_mm = measure_distance()
        if distance_mm < 2:
            pwm1.duty_u16(32768)
            pwm2.duty_u16(0)
        elif distance_mm > 2:
            pwm1.duty_u16(0)
            pwm2.duty_u16(32768)


    pwm1.duty_u16(0)
    pwm2.duty_u16(0)
    return "stable"

    return "etage1"


def state_etage2(distance_mm):
    while not 2.3 <= distance_mm <= 2.4:
        distance_mm = measure_distance()
        pwm1.duty_u16(32768)
        pwm2.duty_u16(0)

    pwm1.duty_u16(0)
    pwm2.duty_u16(0)
    return "stable"

    return "etage2"



def web_page(state, distance):
    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial; text-align:center; }}
            .button {{
                background-color: #2196F3;
                border: none;
                color: white;
                padding: 16px 40px;
                font-size: 20px;
                margin: 10px;
                cursor: pointer;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>Pico Motor Web-Control</h1>
        <h3>Current State: <b>{state}</b></h3>
        <h3>Distance: <b>{distance:.1f} mm</b></h3>

        <a href="/stue"><button class="button">Go to Stue</button></a><br>
        <a href="/etage1"><button class="button">Go to Etage 1</button></a><br>
        <a href="/etage2"><button class="button">Go to Etage 2</button></a><br>

    </body>
    </html>
    """
    return html



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


def process_web_request(request):
    global web_command
    request = str(request)

    if "/stue" in request:
        web_command = "stue"
    elif "/etage1" in request:
        web_command = "etage1"
    elif "/etage2" in request:
        web_command = "etage2"



def main():
    global state

    while True:
        distance_mm = measure_distance()

        if state == "stable":
            state = state_stable()
        elif state == "stue":
            state = state_stue(distance_mm)
        elif state == "etage1":
            state = state_etage1(distance_mm)
        elif state == "etage2":
            state = state_etage2(distance_mm)


        try:
            conn, addr = s.accept()
            request = conn.recv(1024)
            process_web_request(request)

            response = web_page(state, distance_mm)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except:
            pass

        time.sleep(0.01)


main()



