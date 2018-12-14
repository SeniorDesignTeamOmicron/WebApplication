from django.db import models
from .shoe import Shoe

class SensorReading(models.Model):
    LOCATION_CHOICES = (
        ('T', 'top'),
        ('B', 'bottom')
    )

    pressure = models.FloatField()
    location = models.CharField(max_length=1, choices=LOCATION_CHOICES)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)

    def __str__(self):
        return 'Sensor: {}, Pressure reading: {}, Location: {}'.format(self.id, self.pressure, self.location)