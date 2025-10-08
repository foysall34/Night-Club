# accounts/serializers.py
from rest_framework import serializers

# শুধুমাত্র ডেটা ভ্যালিডেশনের জন্য
class ClubOwnerRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    venue_name = serializers.CharField(required=True)
    venue_address = serializers.CharField(required=True)
    profile_image = serializers.FileField(required=True)
    id_front_page = serializers.FileField(required=True)
    id_back_page = serializers.FileField(required=True)
    link = serializers.CharField(required=False, allow_blank=True, default='')

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()




class LoginSerializer(serializers.Serializer):
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


# --- মূল Event Serializer ---
class EventSerializer(serializers.ModelSerializer):
   
    # GET অনুরোধের উত্তরে ক্লাবের নাম দেখানোর জন্য
    club_name = serializers.StringRelatedField(source='club', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'club', 'club_name', 'name', 'date', 'time', 'entry_fee', 'status', 'created_at']
        extra_kwargs = {
            'club': {'write_only': True} # ইনপুটের সময় শুধু ID নেবে, আউটপুটে দেখাবে না
        }

    def __init__(self, *args, **kwargs):
        """
        Serializer ইনিশিয়ালাইজ করার সময় owner-এর ক্লাবগুলো ফিল্টার করে।
        """
        super().__init__(*args, **kwargs)
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            owner = request.user
            # 'club' ফিল্ডের queryset-কে ফিল্টার করে শুধুমাত্র লগইন করা মালিকের ক্লাবগুলো দেখানো হচ্ছে
            self.fields['club'].queryset = ClubProfile.objects.filter(owner=owner)












from rest_framework import serializers
from .models import LegalContent

class LegalContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalContent
    
        fields = ['title', 'content', 'last_updated']