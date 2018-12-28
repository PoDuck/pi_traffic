#!/usr/bin/python
import os
import sys
from time import sleep, time
import RPi.GPIO as GPIO
import socket
import psycopg2
import psycopg2.extras
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controller import I2C_LCD_driver
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


class Line(object):
    def __init__(self, line):
        self.line = ""
        self._current_line = line
        self.scroll = False
        self.update_line(line)
        self.scroll_position = 0

    def update_line(self, line):
        if self.line != line:
            self.line = line
            if len(line) > 16:
                self.scroll = True
            else:
                self.scroll = False
            padding = " " * (16 - len(line))
            self._current_line = (line + padding)[:16]
            self.scroll_position = 0

    def get_line(self):
        return self._current_line

    def cycle(self):
        if self.scroll:
            if self.scroll_position >= len(self.line) + 3:
                self.scroll_position = 0
            end = self.line[:self.scroll_position]
            start = self.line[self.scroll_position:]
            if self.scroll_position > len(self.line):
                end_dots = self.scroll_position - len(self.line)
                start_dots = 3 - end_dots
            else:
                start_dots = 3
                end_dots = 0
            line = start + " " * start_dots + end + " " * end_dots
            self._current_line = line[:16]
            if settings.DEBUG:
                print(self._current_line)
            self.scroll_position += 1


class Lcd(object):
    def __init__(self, database):
        self.db = database
        self.lcd_query = "SELECT * FROM public.lcd_lcd WHERE active = 'True';"
        self.lcd_data = {}
        self.last_db_test = None
        self.new_line = False
        self.line_1 = None
        self.line_2 = None
        self.power_switch_pin = None
        self.lcd = None
        self.start_data = {}
        self.db_check()
        self.last_output_time = time()
        self.start_data = self.lcd_data
        if self.lcd_data:
            self.lcd = I2C_LCD_driver.lcd()
            self.line_1 = Line(self.lcd_data['line_1'])
            self.line_2 = Line(self.lcd_data['line_2'])

    def db_check(self):
        cursor = self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(self.lcd_query, ([]))
        if cursor.rowcount:
            lcd_data = cursor.fetchall()[0]
            if lcd_data != self.lcd_data:
                self.lcd_data = lcd_data
                self.new_line = True
        else:
            self.lcd_data = {}
        self.last_db_test = time()
        if self.lcd_data:
            if self.lcd_data['power_switch_pin']:
                GPIO.setup(self.lcd_data['power_switch_pin'], GPIO.OUT)
                GPIO.output(self.lcd_data['power_switch_pin'], GPIO.HIGH)

    def mode_switch(self, mode):
        if self.lcd_data['show_mode']:
            if self.lcd_data['mode_line'] == 1:
                self.line_1.update_line("Mode: " + mode)
            else:
                self.line_2.update_line("Mode: " + mode)
        else:
            if self.lcd_data['mode_line'] == 1:
                self.line_1.update_line(self.lcd_data['line_1'])
            else:
                self.line_2.update_line(self.lcd_data['line_2'])

    def cycle(self, mode):
        now = time()
        if now - self.last_db_test > 5:
            self.db_check()
            if self.lcd_data != self.start_data:
                self.line_1.update_line(self.lcd_data['line_1'])
                self.line_2.update_line(self.lcd_data['line_2'])
                self.start_data = self.lcd_data
        if now - self.last_output_time >= 0.5:
            self.line_1.cycle()
            self.line_2.cycle()
            self.lcd.lcd_display_string(self.line_1.get_line(), 1)
            self.lcd.lcd_display_string(self.line_2.get_line(), 2)
            self.last_output_time = now


class Display(object):
    def __init__(self):
        self.db = psycopg2.connect(host=settings.DATABASES['default']['HOST'],
                                   database=settings.DATABASES['default']['NAME'],
                                   user=settings.DATABASES['default']['USER'],
                                   password=settings.DATABASES['default']['PASSWORD'])
        self.lcd = Lcd(self.db)
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
                switches_switch.pull,
                switches_switch.on_name,
                switches_switch.off_name
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
                'on': switch[3],
                'off': switch[4],
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
                        'on': switch[3],
                        'off': switch[4],
                    }
                self.last_switch_fetch = switches
                self.reset_lights()
            if self.sequence != current_sequence:
                self.sequence = current_sequence
                self.reset_lights()
            self.db_last_accessed = now

    def update_ip(self, lcd_id, ip, line):
        """ update ip based on the id """
        sql = "UPDATE lcd_lcd SET " + line + " = %s WHERE id = %s;"
        cursor = self.db.cursor()
        cursor.execute(sql, ("IP Address: " + ip, lcd_id))
        updated_rows = cursor.rowcount
        self.db.commit()
        return updated_rows

    def line_scroll(self, text, line):
        pass

    def lcd_cycle(self, position):
        if position:
            mode = self.switches['mode']['on']
        else:
            mode = self.switches['mode']['off']
        self.lcd.cycle(mode)

    def current_switch_position(self):
        return GPIO.input(self.switches['mode']['pin'])

    def main_cycle(self):
        while True:
            self.lcd_cycle(self.current_switch_position())
            self.db_test()
            if self.current_switch_position() != self.last_switch_position:
                self.reset_lights()
                self.last_switch_position = self.current_switch_position()
            if GPIO.input(self.switches['mode']['pin']) == self.switches['mode']['pull']:
                self.music_cycle()
                self.lcd.mode_switch(self.switches['mode']['on'])
            else:
                self.light_cycle()
                self.lcd.mode_switch(self.switches['mode']['off'])


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
