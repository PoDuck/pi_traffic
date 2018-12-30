from django.db import models


class TrackedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Light(TrackedModel):
    color = models.CharField(max_length=255, help_text="This can be a color, or any description of the light, such as 'Yellow Arrow'")
    pin = models.IntegerField(help_text="BCM mode pin number of the switch.  Not the physical pin number.")
    delay = models.FloatField(help_text="Amount of time from the start of the cycle until this light turns on.")
    duration = models.FloatField(help_text="Length of time this light stays on after it comes on.")
    pull = models.BooleanField(default=False, verbose_name="Pull high", help_text="Check the box if the light should be pulled high when it is on.")
