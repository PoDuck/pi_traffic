from django.db import models


SWITCH_TYPES = [
    (0, 'Mode'),
    (1, 'Sound Sensor'),
]


class TrackedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Switch(TrackedModel):
    name = models.CharField(max_length=200, help_text="Give a friendly name to this switch.")
    pin = models.IntegerField(help_text="GPIO Pin to look for.  This is in BCM mode.")
    pull = models.BooleanField(default=False, verbose_name="Pulls high", help_text="Check the box if the switch pulls the pin high when it is on.")
    on_name = models.CharField(max_length=255, help_text="Function when switch is on.", default="", blank=True)
    off_name = models.CharField(max_length=255, help_text="Function when switch is off.", default="", blank=True)
    switch_type = models.IntegerField(choices=SWITCH_TYPES, default=0)
