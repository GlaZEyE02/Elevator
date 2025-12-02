try:
    import usocket as socket
except:
    import socket

import time
from machine import Pin, PWM


spinPin1 = Pin(0, Pin.OUT)
spinPin2 = Pin(1, Pin.OUT)
pwm1 = PWM(spinPin1)
pwm2 = PWM(spinPin2)
pwm1.freq(50)
pwm2.freq(50)


gy53 = Pin(16, Pin.IN)


button1 = Pin(2, Pin.IN, Pin.PULL_UP)
button2 = Pin(3, Pin.IN, Pin.PULL_UP)
button3 = Pin(4, Pin.IN, Pin.PULL_UP)


def measure_distance():
    while gy53.value() == 0:
        pass
    starttime = time.ticks_us()

    while gy53.value() == 1:
        pass
    endtime = time.ticks_us()
    pulse_width_us = time.ticks_diff(endtime, starttime)
    distance_mm = pulse_width_us
    distance_mm = distance_mm / 1000
    return distance_mm

def read_buttons():
    if button1.value() == 0:
        return "stue"
    elif button2.value() == 0:
        return "etage1"
    elif button3.value() == 0:
        return "etage2"
    else:
        return None


def state_stable(distance_mm):
    pwm1.duty_u16(0)
    pwm2.duty_u16(0)

    button_state = read_buttons()
    if button_state:
        return button_state
    return "stable"

def state_stue(distance_mm):
    pwm1.duty_u16(0)
    pwm2.duty_u16(32768)

    if distance_mm < 100:
        pwm1.duty_u16(0)
        pwm2.duty_u16(0)
        return "stable"
    return "stue"

def state_etage1(distance_mm):
    if distance_mm < 200:
        pwm1.duty_u16(32768)
        pwm2.duty_u16(0)
    elif distance_mm > 200:
        pwm1.duty_u16(0)
        pwm2.duty_u16(32768)


    if 195 <= distance_mm <= 205:
        pwm1.duty_u16(0)
        pwm2.duty_u16(0)
        return "stable"

    return "etage1"

def state_etage2(distance_mm):
    pwm1.duty_u16(32768)
    pwm2.duty_u16(0)

    if 295 <= distance_mm <= 305:
        pwm1.duty_u16(0)
        pwm2.duty_u16(0)
        return "stable"
    return "etage2"



def main():
    state = "stable"

    while True:
        distance_mm = measure_distance()

        if state == "stable":
            state = state_stable(distance_mm)
        elif state == "stue":
            state = state_stue(distance_mm)
        elif state == "etage1":
            state = state_etage1(distance_mm)
        elif state == "etage2":
            state = state_etage2(distance_mm)

        time.sleep(0.01)

main()