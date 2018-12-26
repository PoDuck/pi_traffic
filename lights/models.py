from django.db import models


class Light(models.Model):
    color = models.CharField(max_length=255)
    pin = models.IntegerField()
    delay = models.FloatField()
    duration = models.FloatField()
    pull = models.BooleanField(default=False, verbose_name="Pull high", help_text="Check the box if the light should be pulled high when it is on.")
