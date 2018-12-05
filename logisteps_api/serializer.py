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
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class LogistepsUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    left_shoe = ShoeSerializer()
    right_shoe = ShoeSerializer()

    class Meta:
        model = LogistepsUser
        fields = ('user', 'left_shoe', 'right_shoe')

