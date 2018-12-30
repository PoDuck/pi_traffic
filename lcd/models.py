from django.db import models

LINE_CHOICES = [
    (1, 'Line 1'),
    (2, 'Line 2'),
]


class TrackedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Lcd(TrackedModel):
    active = models.BooleanField(verbose_name='Make active screen', default=True, help_text="When checked, this will be the only active LCD.")
    line_1 = models.CharField(max_length=255, verbose_name='Line 1 text', blank=True, null=False, help_text="This text will be displayed as long as you don't override it with an IP address or mode below.")
    line_2 = models.CharField(max_length=255, verbose_name='Line 2 text', blank=True, null=False, help_text="This text will be displayed as long as you don't override it with an IP address or mode below.")
    show_ip = models.BooleanField(verbose_name='Show IP address', default=True, help_text="When checked, this shows the current IP address on the line chosen for the IP address below.")
    ip_line = models.IntegerField(choices=LINE_CHOICES, verbose_name='Line for IP address', default=1, help_text="Which line shows the IP address when above box is checked?")
    show_mode = models.BooleanField(verbose_name='Display mode', default=True, help_text="When checked, this shows the current mode the switch is in on the line chosen for the mode chosen below.")
    mode_line = models.IntegerField(choices=LINE_CHOICES, verbose_name='Line for mode', default=2, help_text="Which line shows the mode if box is checked?")
    power_switch_pin = models.IntegerField(blank=True, null=True, help_text="GPIO pin that turns the LCD on and off.  No pin will be chosen if left blank.")
