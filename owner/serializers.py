# accounts/serializers.py
from rest_framework import serializers
from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable 
from rest_framework import serializers
from .models import ClubOwner
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
from django.conf import settings
import os

class ClubOwnerRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    venue_name = serializers.CharField(required=True)
    venue_city = serializers.CharField(required=True)
    proof_doc = serializers.FileField(required=True)
    profile_image=serializers.FileField(required= True)
    id_front_page = serializers.FileField(required=True)
    id_back_page = serializers.FileField(required=True)

    def validate_email(self, value):
        if ClubOwner.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("your email exist . please press re-send otp.")
        return value

    def create(self, validated_data):
        # Step 1: Geocode location
        geolocator = Nominatim(user_agent="night_club_app")
        full_address = f"{validated_data['venue_name']}, {validated_data['venue_city']}"

        lat, lon = None, None
        try:
            location = geolocator.geocode(full_address, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")

        #  Step 2: Create ClubOwner
        user = ClubOwner.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            venue_name=validated_data['venue_name'],
            venue_city=validated_data['venue_city'],
            profile_image=validated_data['profile_image'],
            proof_doc=validated_data['proof_doc'],
            id_front_page=validated_data['id_front_page'],
            id_back_page=validated_data['id_back_page'],
            latitude=lat,
            longitude=lon
        )

        #  Step 3: Check if venue already exists
        existing_club = ClubProfile.objects.filter(venue_name__iexact=validated_data['venue_name']).first()

        if existing_club:
           
            existing_club.owner = user
            existing_club.save()
            print(f"Existing ClubProfile linked with {user.email}")
        else:
    
            default_image_path = os.path.join(settings.MEDIA_ROOT, 'defaults/default_club.jpg')

            club_profile = ClubProfile.objects.create(
                owner=user,
                venue_name=validated_data['venue_name'],
                venue_city=validated_data['venue_city'],
                club_location=validated_data['venue_city'],
                latitude=lat,
                longitude=lon,
                email=validated_data['email'],
                phone=validated_data['phone_number'],
            )

    
            if os.path.exists(default_image_path):
                with open(default_image_path, 'rb') as f:
                    club_profile.clubImageUrl.save('default_club.jpg', ContentFile(f.read()), save=True)

            print(f"New ClubProfile created for {user.email}")

        return user







class ClubOwnerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubOwner
        fields = ['id', 'email', 'verification_status']



class OwnerVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=4)

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()




class  LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

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
        fields = ['id', 'name', 'club_name', 'owner_name', 'date', 'time', 'entry_fee', 'status', 'created_at']






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
        


#=============================================================================
#=============================================================================
#===========================================================================
# for follow  & follwers
from rest_framework import serializers
from .models import User

class UserFollowSerializer(serializers.ModelSerializer):


    follow_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'follow_status'] 

    def get_follow_status(self, obj):
     
        request_user = self.context.get('request').user
        if not request_user.is_authenticated or request_user == obj:
            return None 

       
        is_following = request_user.following.filter(pk=obj.pk).exists()

        is_followed_by = request_user.followers.filter(pk=obj.pk).exists()

        if is_following:
   
            return 'unfollow'
        elif is_followed_by:
        
            return 'follow_back'
        else:
            
            return 'follow'
        

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