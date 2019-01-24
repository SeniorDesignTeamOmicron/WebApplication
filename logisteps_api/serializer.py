from rest_framework import serializers
from logisteps.models import Location, Shoe, Step, LogistepsUser, SensorReading
from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault
from mysite import settings

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ('id', 'latitude', 'longitude')

class ShoeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shoe
        fields = ('size', 'foot')
    
    def update(self, instance, validated_data):
        instance.size = validated_data.get('size', instance.size)
        instance.foot = validated_data.get('foot', instance.foot)

        instance.save()

        return instance

class SensorReadingSerializer(serializers.ModelSerializer):
    shoe = serializers.CharField()

    class Meta:
        model = SensorReading
        fields = ('pressure', 'location', 'shoe')
    
    def create(self, validated_data):
        shoe_data = validated_data.pop('shoe')

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {'validators': []},
        }

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
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
        fields = ('user', 'left_shoe', 'right_shoe', 'height', 'weight', 'step_goal')
        lookup_field = 'user__username'
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        right_shoe_data = validated_data.pop('right_shoe')
        left_shoe_data = validated_data.pop('left_shoe')

        user = User.objects.create_user(**user_data)
        right_shoe = Shoe.objects.create(**right_shoe_data)
        left_shoe = Shoe.objects.create(**left_shoe_data)
        logistepsUser = LogistepsUser.objects.create(user=user, right_shoe=right_shoe, left_shoe=left_shoe, **validated_data)
        return logistepsUser

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_obj = User.objects.get(username=user_data["username"])
        instance.user = UserSerializer.update(UserSerializer(), user_obj, user_data)

        logistepsUser_obj = LogistepsUser.objects.get(user_id=user_obj.id)

        left_shoe_obj = Shoe.objects.get(id=logistepsUser_obj.left_shoe_id)
        instance.left_shoe = ShoeSerializer.update(ShoeSerializer(), left_shoe_obj, validated_data.pop('left_shoe'))

        right_shoe_obj = Shoe.objects.get(id=logistepsUser_obj.right_shoe_id)
        instance.right_shoe = ShoeSerializer.update(ShoeSerializer(), right_shoe_obj, validated_data.pop('right_shoe'))

        instance.height = validated_data.get('height', instance.height)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.step_goal = validated_data.get('step_goal', instance.step_goal)

        instance.save()
        return instance

class StepSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    sensor_reading = SensorReadingSerializer()
    datetime = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = Step
        fields = ('datetime', 'sensor_reading', 'location')
    
    def create(self, validated_data):
        location_data = validated_data.pop('location')
        sensor_reading_data = validated_data.pop('sensor_reading')
        shoe_data = sensor_reading_data.pop('shoe')

        username =  self.context['request'].user
        user = User.objects.get(username=username)
        logistepsUser = LogistepsUser.objects.get(user_id=user.id)

        if(shoe_data == "right"):
            shoe_obj = Shoe.objects.get(pk=logistepsUser.right_shoe_id)
        else:
            shoe_obj = Shoe.objects.get(pk=logistepsUser.left_shoe_id)

        location = Location.objects.create(**location_data)
        sensor_reading_obj = SensorReading.objects.create(**sensor_reading_data, shoe=shoe_obj)
        step = Step.objects.create(**validated_data, user=logistepsUser, location=location, sensor_reading=sensor_reading_obj)
        return step

# class StepSummary(serializers.BaseSerializer):
