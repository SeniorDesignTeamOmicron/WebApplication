from django.db import models

class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def save(self, *args, **kwargs):
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return 'ID: {}, Latitude: {}, Longitude: {}'.format(self.id, self.latitude, self.longitude)
