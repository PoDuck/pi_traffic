from django.db import models

LINE_CHOICES = [
    (1, 'Line 1'),
    (2, 'Line 2'),
]


class Lcd(models.Model):
    active = models.BooleanField(verbose_name='Make active screen', default=True)
    line_1 = models.CharField(max_length=255, verbose_name='Line 1 text', blank=True, null=False)
    line_2 = models.CharField(max_length=255, verbose_name='Line 2 text', blank=True, null=False)
    show_ip = models.BooleanField(verbose_name='Show IP address', default=True)
    ip_line = models.IntegerField(choices=LINE_CHOICES, verbose_name='Line for IP address', default=1)
    show_mode = models.BooleanField(verbose_name='Display mode', default=True)
    mode_line = models.IntegerField(choices=LINE_CHOICES, verbose_name='Line for mode', default=2)
    power_switch_pin = models.IntegerField(blank=True, null=True)
