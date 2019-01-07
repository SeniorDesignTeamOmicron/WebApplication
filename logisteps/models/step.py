from django.db import models
from .sensorReading import SensorReading
from .location import Location
from .logistepsUser import LogistepsUser

class Step(models.Model):
    datetime = models.DateTimeField(auto_now=False, auto_now_add=False)
    sensor_reading = models.OneToOneField(SensorReading, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(LogistepsUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Logisteps Step"
        verbose_name_plural = "Logisteps Steps"

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.sensor_reading.delete()
        self.location.delete()
        return super().delete(*args, **kwargs)