#!/usr/bin/python
# import subprocess
from controller.config import *
from time import sleep, time
import RPi.GPIO as GPIO
from threading import Event
from controller import I2C_LCD_driver
import socket
import psycopg2
from pi_traffic.settings import DATABASES


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Change port to a port that you do not have in use.
    s.connect(("8.8.8.8", 8080))
    ip = s.getsockname()[0]
    s.close()
    return ip


class Light(object):
    """
    Parent class for all lights.
    """
    # Private: Is power on or off
    _power = None
    # Private: Length of time light is on
    _duration = None
    # Private: color of light
    _color = None
    arrow_delay = 0
    pin = None
    start_time = None
    _delay = 0

    def __init__(self, sequence):
        """
        Initialize light
        :param lights: dictionary of {color: GPIO_pin, ...}
        :param sequence: tuple of (color, delay, duration)
        """
        self._color = sequence[0]
        self._delay = sequence[1]
        self._duration = sequence[2]
        self.pin = sequence[3]
        self._power = False
        GPIO.setup(self.pin, GPIO.OUT)
        self.start_time = time()

    def toggle_power(self):
        """
        Turn power on or off depending on current status
        :return: None
        """
        if self._power:
            self.off()
        else:
            self.on()

    def cycle(self):
        """
        Turn light on, wait for the specified duration, and shut light off.  Watches e for event handling.
        :return: None
        """
        now = time()
        elapsed = now - self.start_time
        if self._delay <= elapsed <= (self._delay + self._duration):
            if not self._power:
                self.on()
        elif self._power:
            self.off()

    def on(self):
        """
        Turns light on
        :return: None
        """
        GPIO.output(self.pin, GPIO.LOW)
        if DEBUG:
            print(self.get_color() + " on")
        self._power = True

    def off(self):
        """
        Turns light off
        :return: None
        """
        GPIO.output(self.pin, GPIO.HIGH)
        if DEBUG:
            print(self.get_color() + " off")
        self._power = False

    def get_color(self):
        """
        :return: str(light color)
        """
        return self._color

    def status(self):
        """
        Returns True if power is on to light.
        :return:
        """
        return self._power


class TrafficSignal(object):
    """
    Main light control object.  Initializes all lights and sets things up to be sequenced.
    """
    light_event = Event()
    switch_on = None
    light_list = None
    lights = []
    powered = []
    music_triggered = False
    current_music_mode = None
    previous_switch = None
    lights_on = False

    def __init__(self, sensors):
        """
        TrafficSignal initialization
        :param pins: Dictionary containing values in {color: GPIO_pin} format.
        :param sensors: Dictionary containing values for 'switch' and 'music' GPIO pins
        """
        self.sensors = sensors
        self.db = psycopg2.connect(host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'], user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'])
        cur = self.db.cursor()
        cur.execute('SELECT lights_light.color, lights_light.delay, lights_light.duration, lights_light.pin FROM public.lights_light;')
        self.sequence = cur.fetchall()
        if USE_LCD:
            self.screen = I2C_LCD_driver.lcd()
            self.line1_string = "IP Address: " + get_ip_address()
            self.lcd_pad = " " * 16
            self.lcd_time = time() * 1000
        self.sequence_reset()
        if GPIO.input(sensors['switch']):
            self.switch_on = True
            self.mode = "Music"
        else:
            self.switch_on = False
            self.mode = "Traffic"
        self.all_lights_off()
        for light in self.lights:
            light.on()
            sleep(.5)
            light.off()
        sleep(1)

        self.start_mode = self.mode
        if USE_LCD:
            self.screen.lcd_display_string("Mode: " + self.mode, 2)
            if DEBUG:
                print("Mode: " + self.mode)
            self.ip_max = len(self.line1_string)
            self.lcd_pos = 0

    def switch_detect(self, channel):
        """
        Callback for mode switch
        :param channel: GPIO Channel
        :return: None
        """
        if GPIO.input(self.sensors['switch']):
            self.switch_on = True
            self.light_event.set()
            self.mode = "Music"
            if DEBUG:
                print("Rising edge detected.")
                print("Do music stuff.\n")
        else:
            self.switch_on = False
            self.light_event.clear()
            self.mode = "Traffic"
            self.initialize()
            if DEBUG:
                print("Falling edge detected.")
                print("Lights initialized")

    def all_lights_off(self):
        """
        Turn all lights off
        :return: None
        """
        for light in self.lights:
            light.off()
        self.lights_on = False
        if DEBUG:
            print("All lights off")

    def all_lights_on(self):
        """
        Turn all lights on
        :return: None
        """
        for light in self.lights:
            light.on()
        self.lights_on = True
        if DEBUG:
            print("all lights on")

    def initialize(self):
        """
        Resets all light timings to now.
        :return: None
        """
        start_time = time()
        for light in self.lights:
            light.start_time = start_time

    def music_detect(self, channel):
        """
        Callback for music sensor switch.
        :param channel: GPIO Channel
        :return: None
        """
        self.music_triggered = True
        # If music sensor pulled high turn off lights
        self.current_music_mode = GPIO.input(self.sensors['music'])

    def sequence_reset(self):
        self.all_lights_off()
        self.lights = []
        self.powered = []
        for sequence in self.sequence:
            self.lights.append(Light(sequence))
            self.powered.append(False)

    def cycle(self):
        while True:
            if USE_LCD:
                self.lcd_tick()
            # Check if switch is in a different position, and if so shut off lights
            current_switch = GPIO.input(SENSORS['switch'])
            if current_switch != self.previous_switch:
                self.all_lights_off()

            # Check if in music mode
            # if self.switch_on:
            if not True:
                if GPIO.input(SENSORS['music']) == GPIO.LOW:
                    if self.lights_on:
                        self.all_lights_off()
                else:
                    if not self.lights_on:
                        self.all_lights_on()
            else:  # In traffic mode
                cur = self.db.cursor()
                cur.execute('SELECT lights_light.color, lights_light.delay, lights_light.duration, lights_light.pin FROM public.lights_light;')
                new_sequence = cur.fetchall()
                if self.sequence != new_sequence:
                    self.sequence = new_sequence
                    self.sequence_reset()
                if self.previous_switch:
                    self.initialize()
                if not self.light_event.is_set():
                    i = 0
                    if True not in self.powered:
                        self.initialize()
                    for light in self.lights:
                        light.cycle()
                        self.powered[i] = light.status()
                        i += 1
                else:
                    self.all_lights_off()
            self.previous_switch = current_switch

    def lcd_tick(self):
        now = time() * 1000
        delay = 500
        # If last lcd event was over delay ms ago, and lcd position is inside the length of line 1
        if now - self.lcd_time > delay and self.lcd_pos in range(0, len(self.line1_string)):
            self.screen.lcd_display_string(self.lcd_pad, 1)
            lcd_text = self.line1_string[self.lcd_pos:(self.lcd_pos + 16)]
            self.screen.lcd_display_string(lcd_text, 1)
            if DEBUG:
                print(lcd_text)
            if self.mode != self.start_mode:
                self.screen.lcd_display_string(self.lcd_pad, 2)
                self.screen.lcd_display_string("Mode: " + self.mode, 2)
                if DEBUG:
                    print("Mode: " + self.mode)
                self.start_mode = self.mode
            self.lcd_pos += 1
            # if position is greater than the length of the line 1 string, reset position.
            if self.lcd_pos > len(self.line1_string) - 1:
                self.lcd_pos = 0
            self.lcd_time = now


def main():
    print(get_ip_address())
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SENSORS['music'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSORS['switch'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # initialize lights
    lights = TrafficSignal(SENSORS)

    # Setup callback for switch.
    GPIO.add_event_detect(SENSORS['switch'], GPIO.BOTH, callback=lights.switch_detect)

    try:
        # Start light cycle.
        lights.cycle()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    main()