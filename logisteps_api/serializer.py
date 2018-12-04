from rest_framework import serializers
from logisteps.models import Location, Shoe, Step, LogistepsUser
from django.contrib.auth.models import User

class LocationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'owner')

class ShoeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shoe
        fields = ('size', 'is_left')

class UserSerializer(serializers.ModelSerializer):
    locations = serializers.PrimaryKeyRelatedField(many=True, queryset=Location.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'locations')
