import time
from time import sleep
from machine import Pin
from machine import PWM

spinPin1 = Pin(0, Pin.OUT)
spinPin2 = Pin(1, Pin.OUT)
pwm1 = PWM(spinPin1, freq=20, duty_u16=8192)
pwm2 = PWM(spinPin2, freq=20, duty_u16=8192)
gy53 = Pin(16, Pin.OUT)

pwm1.duty_u16(32768)
pwm2.duty_u16(32768)

while True:
    while gy53.value() == 0:
        pass

    starttime = time.ticks_us()

    while gy53.value() == 1:
        pass

    endtime = time.ticks_us()
    pulse_width_us = time.ticks_diff(endtime, starttime)
    distance_mm = pulse_width_us
    distance_m = distance_mm / 1000.0

    def off():
        pwm1.duty_u16(0)
        pwm2.duty_u16(0)
        sleep(5)

    def left(time):
        pwm1.duty_u16(0)
        pwm2.duty_u16(32768)
        sleep(time)

    def right(time):
        pwm2.duty_u16(0)
        pwm1.duty_u16(32768)
        sleep(time)

    def main():
        while True:
            print("Spin Time left :D")
            left(5)
            sleep(2)
            print("Spin Time right :D")
            right(5)
            sleep(2)
            print("Spin Time off :D")
            off()
            sleep(2)

#abe

main()