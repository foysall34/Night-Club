# accounts/serializers.py
from rest_framework import serializers
from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable 

from rest_framework import serializers

class ClubOwnerRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    venue_name = serializers.CharField(required=True)
    venue_address = serializers.CharField(required=True)
    venue_city = serializers.CharField(required=True)
    profile_image = serializers.FileField(required=True)
    id_front_page = serializers.FileField(required=True)
    id_back_page = serializers.FileField(required=True)
    link = serializers.CharField(required=False, allow_blank=True, default='')


    def validate_email(self, value):
        """
        Check that the email is not already in use.
        """
        if ClubOwner.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return value

    def create(self, validated_data):
        """
        Create and return a new ClubOwner instance, with geocoded lat/lon.
        """
     
        geolocator = Nominatim(user_agent="owner") 
        full_address = f"{validated_data['venue_address']}, {validated_data['venue_city']}"
        
        lat = None
        lon = None
        try:
            location = geolocator.geocode(full_address, timeout=10) 
            if location:
                lat = location.latitude
                lon = location.longitude
                print(f"Coordinates found for {full_address}: ({lat}, {lon})")
            else:
                print(f"Could not find coordinates for: {full_address}")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
  
            print(f"Geocoding service error: {e}")
        except Exception as e:
          
            print(f"An unexpected error occurred during geocoding: {e}")


    def create(self, validated_data):
        """
        Create and return a new ClubOwner instance, given the validated data.
        """
     
        user = ClubOwner.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            venue_name=validated_data['venue_name'],
            venue_address=validated_data['venue_address'],
            venue_city=validated_data['venue_city'],
            profile_image=validated_data['profile_image'],
            id_front_page=validated_data['id_front_page'],
            id_back_page=validated_data['id_back_page'],
            link=validated_data.get('link', ''),
            latitude=lat,    
            longitude=lon  ,
        )
        return user


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
# api/serializers.py

from rest_framework import serializers
from .models import ClubProfile

from rest_framework import serializers
from .models import ClubProfile, ClubType, Vibes_Choice,ClubOwner




# owner/serializers.py

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
            'id', 'owner', 'clubName', 'dressCode', 'ageRequirement', 'coverCharge',
            'clubImageUrl', 'features', 'events', 'practicalInfo', 'contact',
            'club_type', 'vibes_type',
            'club_type_ids', 'vibes_type_ids'
        ]
        read_only_fields = ('owner',)
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)






# for weekly hours 
# owner/serializers.py

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


class OwnerClubSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = ClubProfile
        fields = ['id', 'clubName']



class EventSerializer(serializers.ModelSerializer):
   
 
    club_name = serializers.StringRelatedField(source='club', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'club', 'club_name', 'name', 'date', 'time', 'entry_fee', 'status', 'created_at']
        extra_kwargs = {
            'club': {'write_only': True} 
        }

    def __init__(self, *args, **kwargs):
    
        super().__init__(*args, **kwargs)
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            owner = request.user
  
            self.fields['club'].queryset = ClubProfile.objects.filter(owner=owner)



from rest_framework import serializers
from .models import LegalContent

class LegalContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalContent
    
        fields = ['title', 'content', 'last_updated']






# clubs/serializers.py
# from rest_framework import serializers




# write your review here





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
        # is_active will be False by default as set in the model
        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords must match.")
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def save(self):
        # uidb64 and token are passed through context from the view
        uidb64 = self.context.get('uidb64')
        token = self.context.get('token')
        password = self.validated_data['password']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(password)
            user.save()
            return user
        else:
            raise serializers.ValidationError("Reset link is invalid or has expired.")