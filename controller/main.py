#!/usr/bin/python
import os
import sys
from time import sleep, time
import RPi.GPIO as GPIO
import socket
import psycopg2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pi_traffic import settings


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

    def __init__(self, sequence):
        self._color = sequence[0]
        self._delay = sequence[1]
        self._duration = sequence[2]
        self._pin = sequence[3]
        self.start_time = time()
        self.total_time = self._delay + self._duration
        self._finished = False
        GPIO.setup(self._pin, GPIO.OUT)

    def on(self):
        """
        Turns light on
        :return: None
        """
        if self.status() == GPIO.HIGH:
            GPIO.output(self._pin, GPIO.LOW)
            if settings.DEBUG:
                print(self.get_color() + " on")

    def off(self):
        """
        Turns light off
        :return: None
        """
        if self.status() == GPIO.LOW:
            GPIO.output(self._pin, GPIO.HIGH)
            if settings.DEBUG:
                print(self.get_color() + " off")

    def toggle_power(self):
        if self.status():
            self.off()
        else:
            self.on()

    def cycle(self):
        """
        Turn light on, wait for the specified duration, and shut light off.  Watches e for event handling.
        :return: None
        """
        now = time()
        elapsed_time = now - self.start_time
        if self._delay <= elapsed_time <= self.total_time:
            self.on()
        else:
            if elapsed_time >= self.total_time:
                self._finished = True
            self.off()

    def reset(self, start_time):
        self._finished = False
        self.start_time = start_time
        self.off()

    def get_color(self):
        return self._color

    def status(self):
        return GPIO.input(self._pin)

    def finished(self):
        return self._finished


class Display(object):
    def __init__(self):
        self.db = psycopg2.connect(host=settings.DATABASES['default']['HOST'],
                                   database=settings.DATABASES['default']['NAME'],
                                   user=settings.DATABASES['default']['USER'],
                                   password=settings.DATABASES['default']['PASSWORD'])
        cursor = self.db.cursor()
        self.sequence_query = """
                SELECT lights_light.color,
                lights_light.delay,
                lights_light.duration,
                lights_light.pin
                FROM public.lights_light;
                """
        self.switches_query = """
                SELECT switches_switch.name,
                switches_switch.pin,
                switches_switch.pull
                FROM public.switches_switch;
                """
        cursor.execute(self.sequence_query)
        self.sequence = cursor.fetchall()
        cursor = self.db.cursor()
        cursor.execute(self.switches_query)
        switches = cursor.fetchall()
        self.last_switch_fetch = switches
        self.switches = {}
        for switch in switches:
            if switch[2]:
                pull = GPIO.HIGH
            else:
                pull = GPIO.LOW
            self.switches[switch[0]] = {
                'pin': switch[1],
                'pull': pull,
            }
        if self.switches['music']['pull']:
            initial = GPIO.PUD_DOWN
        else:
            initial = GPIO.PUD_UP
        GPIO.setup(self.switches['music']['pin'], GPIO.IN, pull_up_down=initial)
        if self.switches['mode']['pull']:
            initial = GPIO.PUD_DOWN
        else:
            initial = GPIO.PUD_UP
        GPIO.setup(self.switches['mode']['pin'], GPIO.IN, pull_up_down=initial)
        self.db_last_accessed = time()
        self.lights = []
        self.last_switch_position = GPIO.input(self.switches['mode']['pin'])
        for s in self.sequence:
            self.lights.append(Light(s))
        for light in self.lights:
            light.on()
            sleep(0.5)
            light.off()
        sleep(1)
        self.reset_timings()

    def all_lights_off(self):
        for light in self.lights:
            light.off()

    def all_lights_on(self):
        for light in self.lights:
            light.on()

    def reset_lights(self):
        self.all_lights_off()
        self.lights = []
        for s in self.sequence:
            self.lights.append(Light(s))
        self.reset_timings()

    def reset_timings(self):
        now = time()
        for light in self.lights:
            light.reset(now)

    def light_cycle(self):
        powered = []
        for light in self.lights:
            light.cycle()
            powered.append(light.finished())
        if False not in powered:
            self.reset_timings()

    def music_cycle(self):
        if GPIO.input(self.switches['music']['pin']) == self.switches['music']['pull']:
            self.all_lights_on()
        else:
            self.all_lights_off()

    def db_test(self):
        now = time()
        if now - self.db_last_accessed >= 5:
            cursor = self.db.cursor()
            cursor.execute(self.sequence_query)
            current_sequence = cursor.fetchall()
            cursor = self.db.cursor()
            cursor.execute(self.switches_query)
            switches = cursor.fetchall()
            if self.last_switch_fetch != switches:
                self.switches = {}
                for switch in switches:
                    if switch[2]:
                        pull = GPIO.HIGH
                    else:
                        pull = GPIO.LOW
                    self.switches[switch[0]] = {
                        'pin': switch[1],
                        'pull': pull,
                    }
                self.last_switch_fetch = switches
                self.reset_lights()
            if self.sequence != current_sequence:
                self.sequence = current_sequence
                self.reset_lights()
            self.db_last_accessed = now

    def lcd_cycle(self):
        pass

    def current_switch_position(self):
        return GPIO.input(self.switches['mode']['pin'])

    def main_cycle(self):
        while True:
            self.lcd_cycle()
            self.db_test()
            if self.current_switch_position() != self.last_switch_position:
                self.reset_lights()
                self.last_switch_position = self.current_switch_position()
            if GPIO.input(self.switches['mode']['pin']) == self.switches['mode']['pull']:
                self.music_cycle()
            else:
                self.light_cycle()


def main():
    if settings.DEBUG:
        print(get_ip_address())
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # initialize lights
    lights = Display()

    try:
        # Start light cycle.
        lights.main_cycle()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
