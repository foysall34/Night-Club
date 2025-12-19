# accounts/serializers.py
from datetime import timedelta
from rest_framework import serializers
from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable 
from rest_framework import serializers
from .models import ClubOwner
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
from django.conf import settings
import os
from .utils import get_geoapify_coordinates
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.conf import settings
import os
from .models import ClubOwner, ClubProfile



# serializers.py
from rest_framework import serializers
from .models import ClubOwner


from rest_framework import serializers
from .models import ClubOwner


# accounts/serializers.py
from rest_framework import serializers
from .models import ClubOwner

class OwnerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ClubOwner
        fields = (
            "full_name",
            "email",
            "phone_number",
            "venue_name",
            "venue_address",
            "latitude",
            "password",
            "longitude",
            "proof_doc",
            "profile_image",
            "id_front_page",
            "id_back_page",
        )

    def create(self, validated_data):
        email = validated_data.pop("email") 
        password = validated_data.pop("password")


        owner = ClubOwner.objects.create_user(
            email=email,

            password=password, 
            **validated_data
        )

        owner.is_active = False
        owner.verification_status = "pending"
        owner.save(update_fields=["is_active", "verification_status"])

        return owner















class ClubOwnerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubOwner
        fields = ['id', 'email', 'verification_status']



class OwnerOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            owner = ClubOwner.objects.get(email=data["email"])
        except ClubOwner.DoesNotExist:
            raise serializers.ValidationError("Invalid email")

        if owner.otp != data["otp"]:
            raise serializers.ValidationError("Invalid OTP")

        # OTP expiry: 5 minutes
        from django.utils import timezone
        if timezone.now() - owner.otp_created_at > timedelta(minutes=5):
            raise serializers.ValidationError("OTP expired")

        data["owner"] = owner
        return data


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()



from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import ClubOwner


class OwnerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data["email"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if user.verification_status != "approved":
            raise serializers.ValidationError(
                "Your account is not approved by admin yet"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is inactive"
            )

        data["user"] = user
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password = serializers.CharField(write_only=True)





# For  owner profile club 

from rest_framework import serializers
from .models import ClubProfile
from rest_framework import serializers
from .models import ClubProfile, ClubType, Vibes_Choice,ClubOwner



class CommaSeparatedPKField(serializers.Field):
    def __init__(self, queryset, **kwargs):
        self.queryset = queryset
        super().__init__(**kwargs)
        

        self.error_messages['does_not_exist'] = 'Invalid pk "{pk_value}" - object does not exist.'
        self.error_messages['invalid'] = 'Input must be a comma-separated string of numbers.'
        

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid')
        id_strings = [s.strip() for s in data.split(',') if s.strip()]
        try:
            ids = [int(id_str) for id_str in id_strings]
        except (ValueError, TypeError):
            self.fail('invalid')

        found_objects = self.queryset.filter(pk__in=ids)
        
        if len(ids) != found_objects.count():
            found_ids = found_objects.values_list('pk', flat=True)
            invalid_ids = set(ids) - set(found_ids)
            self.fail('does_not_exist', pk_value=', '.join(map(str, invalid_ids)))

        return found_objects
    def to_representation(self, value):
  
        return None

from geopy.geocoders import Nominatim

class ClubProfileSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    club_type = serializers.StringRelatedField(many=True, read_only=True)
    vibes_type = serializers.StringRelatedField(many=True, read_only=True)

    club_type_ids = CommaSeparatedPKField(
        queryset=ClubType.objects.all(),
        source='club_type',
        write_only=True,
        required=False
    )
    vibes_type_ids = CommaSeparatedPKField(
        queryset=Vibes_Choice.objects.all(),
        source='vibes_type',
        write_only=True,
        required=False
    )

    class Meta:
        model = ClubProfile
        fields = [
            'id', 'owner', 'clubName', 'about', 'dressCode', 'ageRequirement', 'coverCharge',
            'clubImageUrl', 'features', 'events', 'crowd_atmosphere',
            'club_type', 'vibes_type',
            'club_type_ids', 'vibes_type_ids', 'is_favourite',
            'insta_link', 'tiktok_link', 'phone', 'email', 'club_location', 'latitude', 'longitude'
        ]
        read_only_fields = ('owner', 'latitude', 'longitude')

    def _set_lat_lng(self, validated_data):
        """
        Auto populate latitude & longitude from club_location
        """
        location_name = validated_data.get('club_location')
        if location_name:
            geolocator = Nominatim(user_agent="my_app")
            try:
                location = geolocator.geocode(location_name)
                if location:
                    validated_data['latitude'] = location.latitude
                    validated_data['longitude'] = location.longitude
            except Exception as e:
                print(f"Geocoding failed: {e}")

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        self._set_lat_lng(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._set_lat_lng(validated_data)
        return super().update(instance, validated_data)





from .models import ClubType, Vibes_Choice

class ClubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubType
        fields = ['id', 'name']  

class VibesChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vibes_Choice
        fields = ['id', 'name']



class MyClubProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubProfile
        fields = '__all__'


# for weekly hours 
from rest_framework import serializers
from .models import ClubProfile , Event
import re

class WeeklyHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClubProfile
        fields = ['weekly_hours']

    def validate_weekly_hours(self, data):
      
        if not isinstance(data, dict):
            raise serializers.ValidationError("Weekly hours must be a JSON object.")

        REQUIRED_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
   
        for day in REQUIRED_DAYS:
            if day not in data:
                raise serializers.ValidationError(f"Missing data for {day}.")
            
            day_schedule = data[day]
            if not isinstance(day_schedule, dict) or 'start_time' not in day_schedule or 'end_time' not in day_schedule:
                raise serializers.ValidationError(f"Schedule for {day} must be an object with 'start_time' and 'end_time'.")

  
            time_format = re.compile(r'^\d{2}:\d{2}$')
            if not time_format.match(day_schedule['start_time']) or not time_format.match(day_schedule['end_time']):
                raise serializers.ValidationError(f"Time format for {day} must be 'HH:MM'.")

        return data





"""************ For Event & Legal Content ************"""




class EventSerializered(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'date', 'time', 'entry_fee', 'status', 'created_at']


class OwnerClubSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = ClubProfile
        fields = ['id', 'clubName']










class Get_all_EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__' 


from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.clubName', read_only=True)
    owner_name = serializers.CharField(source='club.owner.full_name', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'club_name', 'owner_name', 'date', 'time', 'entry_fee', 'status', 'created_at']






from rest_framework import serializers
from .models import LegalContent

class LegalContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalContent
    
        fields = ['title', 'content', 'last_updated']




#=============================================================================
#=============================================================================
#=========================================================================
"""************ For Custom User Authentication ************"""
#=============================================================================
#=============================================================================
#===========================================================================



from rest_framework import serializers
from .models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, force_str

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

class ForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordWithOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    # otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
        


# Infobip OTP Serializer

from rest_framework import serializers

class SendMobileOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_phone_number(self, value):
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code, e.g. +14155551234")
        return value





from .models import UserLocation

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ['latitude', 'longitude']





#=============================================================================
#=============================================================================
#===========================================================================
# for follow  & follwers
from rest_framework import serializers
from .models import User


class UserFollowSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    follow_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "follow_status"]

    def get_full_name(self, obj):
        full_name = getattr(obj, "full_name", None)
        if full_name:
            return full_name
        # fallback for users without .full_name field
        return f"{obj.first_name} {obj.last_name}".strip() or "Unnamed User"

    def get_follow_status(self, obj):
        """Check if the requesting/current user already follows this user"""
        request = self.context.get("request")
        current_user = self.context.get("current_user")
        if not current_user:
            return None
        return obj.followers.filter(id=current_user.id).exists()
        

#=========================================================================================
# For user  recomendation data 
#=========================================================================================



from rest_framework import serializers
from geopy.geocoders import Nominatim
from .models import UserProfile, MusicGenre, Vibe, CrowdAtmosphere


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    music_preferences = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=MusicGenre.objects.all()
    )
    ideal_vibes = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Vibe.objects.all()
    )
    crowd_atmosphere = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=CrowdAtmosphere.objects.all()
    )

    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)

    class Meta:
        model = UserProfile
       
        fields = [
            'id',
            'full_name',
            'city', 
            'latitude', 
            'longitude', 
            'music_preferences', 
            'ideal_vibes', 
            'crowd_atmosphere'
        ]
        read_only_fields = ['user']

    def _get_location_from_city(self, city):
        """helper function to get lat/lon from city name"""
        try:
         
            geolocator = Nominatim(user_agent="nightclub_app")
            location = geolocator.geocode(city)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
          
            print(f"Geocoding error: {e}")
        return None, None

    def create(self, validated_data):

        city = validated_data.get('city')
        if city:
            lat, lon = self._get_location_from_city(city)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lon
        

        music_data = validated_data.pop('music_preferences', [])
        vibes_data = validated_data.pop('ideal_vibes', [])
        crowds_data = validated_data.pop('crowd_atmosphere', [])

        profile = UserProfile.objects.create(**validated_data)

        profile.music_preferences.set(music_data)
        profile.ideal_vibes.set(vibes_data)
        profile.crowd_atmosphere.set(crowds_data)

        return profile

    def update(self, instance, validated_data):
     
        city = validated_data.get('city', instance.city)
    
        if 'city' in validated_data and instance.city != city:
            lat, lon = self._get_location_from_city(city)
            instance.latitude = lat
            instance.longitude = lon
        
        instance.city = city
        
     
        if 'music_preferences' in validated_data:
            instance.music_preferences.set(validated_data.get('music_preferences', []))
        if 'ideal_vibes' in validated_data:
            instance.ideal_vibes.set(validated_data.get('ideal_vibes', []))
        if 'crowd_atmosphere' in validated_data:
            instance.crowd_atmosphere.set(validated_data.get('crowd_atmosphere', []))
        
        instance.save()
        return instance
    





# owner recommcodetaion 

from rest_framework import serializers
from .models import ClubProfile, ClubOwner

class ClubDetailSerializer(serializers.ModelSerializer):
    club_id = serializers.IntegerField(source='id', read_only=True)
    full_name = serializers.CharField(source='owner.full_name', read_only=True)
    venue_city = serializers.CharField(source='owner.venue_city', read_only=True)
    latitude = serializers.FloatField(source='owner.latitude', read_only=True)
    longitude = serializers.FloatField(source='owner.longitude', read_only=True)
    practical_info = serializers.JSONField(source='practicalInfo', read_only=True)
    events = serializers.JSONField(read_only=True)
    features = serializers.JSONField(read_only=True)

    class Meta:
        model = ClubProfile
        
        fields = [
            'club_id',
            'full_name',
            'venue_city',
            'latitude',
            'longitude',
            'features',
            'events',
            'practical_info', 
        ]



from rest_framework import serializers
from .models import UserProfile
class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.EmailField(source='user.full_name', read_only=True)
    user_img = serializers.ImageField(read_only=True)
    
    music_preferences = serializers.SlugRelatedField(
        many=True, slug_field='name', read_only=True
    )
    ideal_vibes = serializers.SlugRelatedField(
        many=True, slug_field='name', read_only=True
    )
    crowd_atmosphere = serializers.SlugRelatedField(
        many=True, slug_field='name', read_only=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user_email',
            'user_name' , 
            'user_img',
            'city',
            'latitude',
            'longitude',
            'about',
            'user_reviews',
            'music_preferences',
            'ideal_vibes',
            'crowd_atmosphere',
            'is_online',
            'achievement',
            'followers',
            'created_at'
        ]



class ClubProfileSerializered(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = ClubProfile
        fields = [
            'id',
            'venue_name',
            'venue_city',
            'click_count',
            'owner_email',
        ]





from rest_framework import serializers


class NightclubSerializer(serializers.Serializer):
    place_id = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField(allow_null=True)
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    rating = serializers.FloatField(allow_null=True)
    user_ratings_total = serializers.IntegerField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    website = serializers.URLField(allow_null=True)
    opening_hours = serializers.DictField(child=serializers.ListField(), allow_null=True)
    photos = serializers.ListField(child=serializers.URLField(), allow_empty=True)
    maps_url = serializers.URLField(allow_null=True)