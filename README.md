# Welcome to Pi Traffic

## Installation
This is meant to run on a server ready to run django projects.  You can install it however you want, using whatever server you want, and this will work, as long as you configure your server correctly.  The installation of django does not need to be for the raspberry pi, but there are several tutorials on how to do it, and I'm not looking to reinvent that wheel.

First thing, after installing django, is to install the packages.  Make sure you have also installed pip.  then `pip install -r requirements.txt` will install all the python requirements.

Somewhere in the near future, I will set things up for automatically installing css and javascript dependencies using some package manager.  I'm too lazy to do it right now.  Suffice it to say though, you should install bootstrap 4, font-awesome-free, jquery, and popper into your static files directory.

After that, change the database settings in the settings.py or local_settings.py file to those of your database.  I used postgresql, so you will have to use that, unless you do some work on the code.  You will also need to make sure that your `ALLOWED_HOSTS` are set for being accessed remotely.

## How to use the web interface

There are links across the top to change settings.  Under the lights link, you configure the pins and lights you need for your particular traffic signal.  You should have one light for each light you have connected to your pi.  You should use the BCM mode pin number, and not the physical pin number, when setting the pins.  You also need to know if your relay needs to be pulled high or low in order to turn the light on.  Most solid relay modules are counterintuitively low when on, and high when off.  You can control as many lights as you have GPIO pins on the pi with this.

## Controlling Lights

When deciding the delay and duration, you need to understand that the lights go in a cycle.  The timing is from the beginning of the entire cycle.  For instance, on a five light system, you might want the green arrow to be on 10 seconds before the solid green light comes on, and you might want both of them to be on at the same time for a short period, but you want the green arrow to come on immediately.  That means that your delay for the green arrow is 0, while the delay for the solid green light is 10. 

A sample set of values for a 5 light system might be as follows:

<table style="width: 100%; border-collapse: collapse; height: 108px;" border="1">

<tbody>

<tr style="height: 18px;">

<th style="width: 20%; text-align: center; height: 18px;">Light</th>

<th style="width: 20%; text-align: center; height: 18px;">Pin</th>

<th style="width: 20%; text-align: center; height: 18px;">Delay</th>

<th style="width: 20%; text-align: center; height: 18px;">Duration</th>

<th style="width: 20%; text-align: center; height: 18px;">Pull</th>

</tr>

<tr style="height: 18px;">

<td style="width: 20%; height: 18px;">Green Arrow</td>

<td style="width: 20%; height: 18px;">18</td>

<td style="width: 20%; height: 18px;">0.0</td>

<td style="width: 20%; height: 18px;">10.0</td>

<td style="width: 20%; height: 18px;">LOW</td>

</tr>

<tr style="height: 18px;">

<td style="width: 20%; height: 18px;">Green</td>

<td style="width: 20%; height: 18px;">17</td>

<td style="width: 20%; height: 18px;">5.0</td>

<td style="width: 20%; height: 18px;">25.0</td>

<td style="width: 20%; height: 18px;">LOW</td>

</tr>

<tr style="height: 18px;">

<td style="width: 20%; height: 18px;">Yellow Arrow</td>

<td style="width: 20%; height: 18px;">15</td>

<td style="width: 20%; height: 18px;">10.0</td>

<td style="width: 20%; height: 18px;">5.0</td>

<td style="width: 20%; height: 18px;">LOW</td>

</tr>

<tr style="height: 18px;">

<td style="width: 20%; height: 18px;">Yellow</td>

<td style="width: 20%; height: 18px;">4</td>

<td style="width: 20%; height: 18px;">30.0</td>

<td style="width: 20%; height: 18px;">5.0</td>

<td style="width: 20%; height: 18px;">LOW</td>

</tr>

<tr style="height: 18px;">

<td style="width: 20%; height: 18px;">Red</td>

<td style="width: 20%; height: 18px;">27</td>

<td style="width: 20%; height: 18px;">35.0</td>

<td style="width: 20%; height: 18px;">38.0</td>

<td style="width: 20%; height: 18px;">LOW</td>

</tr>

</tbody>

</table>

You will notice that the delay shows the order in which they will turn on.  The lower the delay, the sooner in the cycle the light will turn on.  Once it is on, it will stay on as long as the duration is set.  The duration starts from the time the light is turned on, not from the beginning of the cycle.  That means, for instance, since the yellow arrow comes on at 10 seconds from the start of the cycle, due to its delay, it will shut off 15 seconds into the cycle, because it stays on for 5 seconds after the initial 10 second wait to turn on.  None of the lights rely on any other light to be on or off.

With this kind of setup, even if you have a full intersection's worth of lights, even pedestrian signals, you can control them individually.

## Controlling Switches

I have designed this to react to switch positions as well.  Unfortunately, it has been necessary to hard code some of this into the program that does the actual work.  That means that if you want to do different things than use a sensor to flash the lights on and off, you will need to modify the code.

Currently, there are two switches.  One is a mode switch that flips it between being a regular traffic signal and reacting to the other switch, which is a sound sensor.  If you want to do more than that, you need to get your hands dirty and edit the code.

## Future Intentions

In the future, I intend to allow some interaction with an LCD screen.  I want to be able to change what is shown on the screen through this web interface.