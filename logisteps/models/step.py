from django.db import models
from .sensorReading import SensorReading
from .location import Location

class Step(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    sensor_reading = models.OneToOneField(SensorReading, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Logisteps Step"
        verbose_name_plural = "Logisteps Steps"

    def __str__(self):
        return self.name