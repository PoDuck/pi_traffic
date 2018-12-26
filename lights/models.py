from django.db import models


class Light(models.Model):
    color = models.CharField(max_length=255)
    pin = models.IntegerField()
    delay = models.FloatField()
    duration = models.FloatField()