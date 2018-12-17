from django.db import models
from django.contrib.auth.models import User
from .shoe import Shoe

# Create your models here.   

class LogistepsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.IntegerField()
    weight = models.IntegerField()
    step_goal = models.IntegerField()
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
        return self.user.username
