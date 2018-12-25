# pi_traffic
Control software to allow raspberry pi to control traffic signal lights, as well as be responsive to music.

This was intended to be connected to an actual traffic light through a relay module, but can be used just to light up LED lights as well.

To use this, all configuration is done in the **config.py** file.  The most important setting, after pin settings for lights and sensors, is the SEQUENCE variable.  It determines how many lights will be controlled, their duration, and the delay before they start.

The config file is well commented, so it should be obvious what each setting is.

**How to install django server**

There is a very good explanation of how to setup a django server with Apache on the Raspberry pi [here](https://mikesmithers.wordpress.com/2017/02/21/configuring-django-with-apache-on-a-raspberry-pi/ "The Anti-Kyte Django on Raspberry Pi tutorial").  Obviously, you will want to configure things for your particular setup.

**How to set timing**

The idea behind delay and duration may not be obvious.  When the traffic signal is initialized, it sets the start time to all lights to the current time.  The time the light comes on is the delay from this initialization.  So, when you want a light to come on at the very beginning of the cycle, its delay is zero.  The amount of time it remains on is its duration.  So, for instance, if you want the green light to come on at t=0, and stay on for 20 seconds, your tuple for the green light would look something like this:

`('green', 0, 20)`

Now, when you look to your yellow light, you will probably want it to go on after the green light goes off, and stay on for 5 seconds, which means it has to start 20 seconds after t=0, so its tuple would look like this:

`('yellow', 20, 5)`

After the yellow light goes off, you may want to start the red light.  That means we need to wait the amount of time the green light was on, plus the amount of time the yellow light was on.  In the real world the red light will be on while the other direction cycles, so its duration will probably be the length of time the green light is on, plus the amount of time the yellow light is on, plus a couple second delay to allow traffic to get out of the intersection.  Therefore we will have something like this for its tuple:

`('red', 25, 27)`

If this is just a three light system, you are done.  Here is your final sequence:

`SEQUENCE = (
    ('green', 0, 20),
    ('yellow', 20, 5),
    ('red', 25, 27)
)`

Keep in mind that half seconds can be used, but the program is designed only to poll the lights to see if they want to change every half second, so the fastest they can change is half a second unless you change that section in the program.

This is just a fun project, and something added I haven't seen other people add before, namely the ability to do more than just sequence traffic lights.