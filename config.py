import os

# Be verbose about what is going on
DEBUG = True

# LCD power switch pin
LCD_POWER = 22

# GPIO Mapping for lights
LIGHTS = {
    'red': 27,
    'yellow': 4,
    'green': 17,
    'left_yellow': 15,
    'left_green': 18,
}

# GPIO Mapping for sensors
SENSORS = {
    'music': 24,
    'switch': 23,
}


# This block of variables is only used in this file for the sequence,
# and can be either disregarded, or changed as needed.
# -------------------------------------------------------- #
# Amount of time after light changes to red before green lights turn on for other direction.
RED_DELAY = 3
# Amount of time green light stays on (affects red light as well)
DURATION = 25
# Amount of time yellow light stays on
YELLOW_DURATION = 5
# Amount of time yellow arrow stays on
YELLOW_ARROW_DURATION = 5
# Amount of time for green arrow to stay on before green solid goes on.
GREEN_ARROW_BEFORE_GREEN_LIGHT = 5
# Amount of time green arrow stays on
GREEN_ARROW_DURATION = 10
# -------------------------------------------------------- #


# (light, delay, duration)
SEQUENCE = [
    ('left_green', 0, GREEN_ARROW_DURATION),
    ('green', GREEN_ARROW_BEFORE_GREEN_LIGHT, DURATION),
    ('left_yellow', GREEN_ARROW_DURATION, YELLOW_ARROW_DURATION),
    ('yellow', GREEN_ARROW_BEFORE_GREEN_LIGHT + DURATION, YELLOW_DURATION),
    ('red', GREEN_ARROW_BEFORE_GREEN_LIGHT + DURATION + YELLOW_DURATION, DURATION + RED_DELAY)
]
