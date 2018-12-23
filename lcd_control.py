#!/usr/bin/python
import RPi.GPIO as GPIO
import I2C_LCD_driver
from config import *
import socket
import fcntl
import struct
from time import sleep

GPIO.setmode(GPIO.BCM)


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])


class LCDControl(object):
    def __init__(self):
        GPIO.setup(SENSORS['switch'], GPIO.IN)
        GPIO.setup(LCD_POWER, GPIO.OUT)
        GPIO.output(LCD_POWER, GPIO.HIGH)
        self.switch_on = GPIO.input(SENSORS['switch'])
        if self.switch_on:
            self.mode = 'Music'
        else:
            self.mode = 'Traffic'

    def lcd_control(self):
        screen = I2C_LCD_driver.lcd()
        line1_string = "IP Address: " + get_ip_address("wlan0")
        str_pad = " " * 16
        start_mode = self.mode
        screen.lcd_display_string("Mode: " + self.mode, 2)
        while True:
            for i in range(0, len(line1_string)):
                lcd_text = line1_string[i:(i + 16)]
                screen.lcd_display_string(lcd_text, 1)
                if self.mode != start_mode:
                    screen.lcd_display_string(str_pad, 2)
                    screen.lcd_display_string("Mode: " + self.mode, 2)
                    start_mode = self.mode
                sleep(0.5)
                screen.lcd_display_string(str_pad, 1)

    def switch_detect(self, channel):
        self.switch_on = GPIO.input(SENSORS['switch'])
        if self.switch_on:
            self.switch_on = True
            self.mode = "Music"
            if DEBUG:
                print("Rising edge detected.")
                print("Do music stuff.\n")
        else:
            self.mode = "Traffic"
            if DEBUG:
                print("Falling edge detected.")


def main():
    # initialize LCD screen
    lcd_screen = LCDControl()

    # Add detection for switch.
    GPIO.add_event_detect(SENSORS['switch'], GPIO.BOTH, callback=lcd_screen.switch_detect)

    try:
        # Start light cycle.
        lcd_screen.lcd_control()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    main()