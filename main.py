#!/usr/bin/python
from config import *
from time import sleep, time
import RPi.GPIO as GPIO
from threading import Event, Thread


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

    def __init__(self, lights, sequence):
        """
        Initialize light
        :param lights: dictionary of {color: GPIO_pin, ...}
        :param sequence: tuple of (color, delay, duration)
        """
        self._color = sequence[0]
        self._delay = sequence[1]
        self._duration = sequence[2]
        self._power = False
        self.pin = lights[self._color]
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

    def __init__(self, pins, sensors, sequence):
        """
        TrafficSignal initialization
        :param pins: Dictionary containing values in {color: GPIO_pin} format.
        :param sensors: Dictionary containing values for 'switch' and 'music' GPIO pins
        :param sequence: List of tuples for each light in the form [(light, delay, duration), ...].
        """
        self.sensors = sensors
        self.sequence = sequence
        self.pins = pins
        for light in sequence:
            self.lights.append(Light(pins, light))
            self.powered.append(False)
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

    def music_cycle(self):
        # If music switch is high, turn lights on.
        if self.music_triggered:
            # Reset music_triggered switch detect
            self.music_triggered = False
            # If switch has been flipped, and music set to high
            if self.current_music_mode:
                # only turn lights on if they are already off.
                if not self.lights_on:
                    self.all_lights_on()
            else:  # Music switch set low
                # only turn lights off if lights are on.
                if self.lights_on:
                    self.all_lights_off()

        # If the current music sensor is different than the last sensor, trigger work.
        # if current_music != self.previous_music:
        #     self.music_triggered = True
        #     self.previous_music = current_music
        #
        #     # If sound is detected turn lights on
        #     if current_music == GPIO.HIGH:
        #         self.all_lights_on()
        #         self.music_triggered = False
        #
        #     # No sound detected, turn lights off
        #     else:
        #         self.all_lights_off()
        #         self.music_triggered = False

    def traffic_light_cycle(self):
        if self.previous_switch:  # If the switch was previously set for music
            self.initialize()  # Reset the light timings
            self.previous_switch = False  # Set previous setting for music to false
        if not self.light_event.is_set():  # If we are in traffic light mode
            i = 0
            if True not in self.powered:  # If no lights are on
                self.initialize()  # Reset timings
            else:
                self.light_event.wait(.5)  # Wait half a second
            for light in self.lights:  # Cycle through all Light objects
                light.cycle()  # run the Light object's cycle
                self.powered[i] = light.status()  # Set whether or not this light has power on.
                i += 1
        else:
            self.all_lights_off()  # Probably won't run, but in case it gets here, the lights should shut off.

    def cycle(self):
        while True:
            if self.switch_on:
                if not self.previous_switch:
                    self.all_lights_off()
                    self.previous_switch = True

                # current_music = GPIO.input(SENSORS['music'])

                self.music_cycle()
            else:
                if self.previous_switch:
                    self.initialize()
                    self.previous_switch = False
                if not self.light_event.is_set():
                    i = 0
                    if True not in self.powered:
                        self.initialize()
                    else:
                        self.light_event.wait(1)
                    for light in self.lights:
                        light.cycle()
                        self.powered[i] = light.status()
                        i += 1
                else:
                    self.all_lights_off()


def main():
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SENSORS['music'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSORS['switch'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # initialize lights
    lights = TrafficSignal(LIGHTS, SENSORS, SEQUENCE)

    # Setup callback for switch.
    GPIO.add_event_detect(SENSORS['switch'], GPIO.BOTH, callback=lights.switch_detect)
    GPIO.add_event_detect(SENSORS['music'], GPIO.BOTH, callback=lights.music_detect)

    # Start LCD

    try:
        # Start light cycle.
        lights.cycle()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
