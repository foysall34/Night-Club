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