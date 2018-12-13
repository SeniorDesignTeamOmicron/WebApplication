from rest_framework import serializers
from logisteps.models import Location, Shoe, Step, LogistepsUser, SensorReading
from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault

class LocationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'owner')

class ShoeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shoe
        fields = ('size', 'foot')

class SensorReadingSerializer(serializers.ModelSerializer):
    shoe = serializers.CharField()

    class Meta:
        model = SensorReading
        fields = ('pressure', 'location', 'shoe')
    
    def create(self, validated_data):
        shoe_data = validated_data.pop('shoe')
        print('***********************')
        print(shoe_data)

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
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        right_shoe_data = validated_data.pop('right_shoe')
        left_shoe_data = validated_data.pop('left_shoe')

        user = User.objects.create_user(**user_data)
        right_shoe = Shoe.objects.create(**right_shoe_data)
        left_shoe = Shoe.objects.create(**left_shoe_data)
        logistepsUser = LogistepsUser.objects.create(user=user, right_shoe=right_shoe, left_shoe=left_shoe)
        return logistepsUser

class StepSerializer(serializers.ModelSerializer):
    # shoe = serializers.CharField()
    location = LocationSerializer()
    sensor_reading = SensorReadingSerializer()

    class Meta:
        model = Step
        fields = ('date', 'time', 'sensor_reading', 'location')

    #def validate(self, data):

    
    def create(self, validated_data):
        location_data = validated_data.pop('location')
        # shoe_data = validated_data.pop('shoe')
        sensor_reading_data = validated_data.pop('sensor_reading')
        shoe_data = sensor_reading_data.pop('shoe')

        # print(shoe_data)
        username =  self.context['request'].user
        user = User.objects.get(username=username)
        logistepsUser = LogistepsUser.objects.get(user_id=user.id)
        print(logistepsUser.id)

        if(shoe_data == "right"):
            shoe_obj = Shoe.objects.get(pk=logistepsUser.right_shoe_id)
        else:
            shoe_obj = Shoe.objects.get(pk=logistepsUser.left_shoe_id)

        location = Location.objects.create(**location_data)
        # sensor_reading_obj = SensorReadingSerializer.create(**sensor_reading_data)
        print(sensor_reading_data)
        sensor_reading_obj = SensorReading.objects.create(**sensor_reading_data, shoe=shoe_obj)
        step = Step.objects.create(**validated_data, location=location, sensor_reading=sensor_reading_obj)
        return step