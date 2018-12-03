from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Location(models.Model):
    latitude = models.models.FloatField()
    longitude = models.models.FloatField()

    def __str__(self):
        return self.name

class Shoe(models.Model):
    size = models.models.DecimalField(max_digits=3, decimal_places=1)
    is_left = models.models.models.BooleanField()

    class Meta:
        verbose_name = "Logisteps Smart Shoe"
        verbose_name_plural = "Logisteps Smart Shoes"

    def __str__(self):
        return self.name
    
class Step(models.Model):
    date = models.models.DateField(auto_now=False, auto_now_add=False)
    time = models.models.TimeField(auto_now=False, auto_now_add=False)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        verbose_name = "Logisteps Step"
        verbose_name_plural = "Logisteps Steps"

    def __str__(self):
        return self.name

class LogistepsUser(models.Model):
    user = models.models.OneToOneField(User, on_delete=models.CASCADE)
    left_shoe = models.models.OneToOneField(
        Shoe,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    right_shoe = models.models.OneToOneField(
        Shoe,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        verbose_name = "LogiSteps User"
        verbose_name_plural = "LogiSteps Users"

    def __str__(self):
        return self.name

