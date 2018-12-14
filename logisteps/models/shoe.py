from django.db import models

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