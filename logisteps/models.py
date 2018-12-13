from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def save(self, *args, **kwargs):
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return 'ID: {}, Latitude: {}, Longitude: {}'.format(self.id, self.latitude, self.longitude)


class Shoe(models.Model):
    FOOT_CHOICES = (
        ('R', 'right'),
        ('L', 'left'),
    )
    size = models.DecimalField(max_digits=3, decimal_places=1)
    foot = models.CharField(max_length=1, choices=FOOT_CHOICES)

    class Meta:
        verbose_name = "Logisteps Smart Shoe"
        verbose_name_plural = "Logisteps Smart Shoes"

    def __str__(self):
        return 'ID: {}, size: {}, foot: {}'.format(self.id, self.size, self.foot)

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
    
class Step(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    # shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    sensor_reading = models.OneToOneField(SensorReading, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Logisteps Step"
        verbose_name_plural = "Logisteps Steps"

    def __str__(self):
        return self.name

class LogistepsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    left_shoe = models.OneToOneField(
        Shoe,
        related_name='user_left_shoe',
        on_delete=models.CASCADE
    )
    right_shoe = models.OneToOneField(
        Shoe,
        related_name='user_right_shoe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "LogiSteps User"
        verbose_name_plural = "LogiSteps Users"

    def __str__(self):
        return self.name
