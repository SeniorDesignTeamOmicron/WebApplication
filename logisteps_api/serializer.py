from rest_framework import serializers
from logisteps.models import Location, Shoe, Step, LogistepsUser

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude')

class ShoeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shoe
        fields = ('size', 'is_left')