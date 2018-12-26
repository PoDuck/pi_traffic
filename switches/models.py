from django.db import models


class Switch(models.Model):
    name = models.CharField(max_length=200, help_text="Give a friendly name to this switch.")
    pin = models.IntegerField(help_text="GPIO Pin to look for.  This is in BCM mode.")
    pull = models.BooleanField(default=False, verbose_name="Pulls high", help_text="Check the box if the switch pulls the pin high when it is on.")
