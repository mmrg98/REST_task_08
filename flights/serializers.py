from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = ['destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):
	flight= serializers.SlugRelatedField(read_only=True , slug_field='destination')
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']


class BookingDetailsSerializer(serializers.ModelSerializer):
	flight= FlightSerializer()
	total= serializers.SerializerMethodField()
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'passengers', 'id','total']

	def get_total(self,obj):
		return obj.passengers * obj.flight.price


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username, first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields=['first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
	tier = serializers.SerializerMethodField()
	past_bookings = serializers.SerializerMethodField()
	user= UserSerializer()
	class Meta:
		model = Profile
		fields = ['user', 'miles','tier','past_bookings']

	def get_tier(self, obj):
		miles_sum=obj.miles
		if miles_sum >= 100000:
			tier = "Platinum"
		elif miles_sum >= 60000 and miles_sum <= 99999:
			tier = "Gold"
		elif miles_sum >= 10000 and miles_sum <= 59999:
			tier = "Silver"
		else:
			tier = "Blue"
		return tier

	def get_past_bookings(self, obj):
		user =obj.user
		bookings = user.bookings.filter(date__lt=timezone.now().date())
		bookings_json=BookingSerializer(bookings, many=True).data
		return bookings_json
