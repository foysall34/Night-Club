# users/serializers.py

from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True,
        required=True # Explicitly making password2 required
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'id_card_front', 'id_card_back', 'face_verification_image'
        ]
        
        # --- FIX: Use extra_kwargs to make all fields required ---
        extra_kwargs = {
            'password': {
                'write_only': True, 
                'required': True
            },
            'username': {'required': True},
            'email': {'required': True},
            
            # This part overrides the model's blank=True, null=True for the API
            'id_card_front': {
                'required': True,
                'allow_null': False
            },
            'id_card_back': {
                'required': True,
                'allow_null': False
            },
            'face_verification_image': {
                'required': True,
                'allow_null': False
            },
        }

    def validate(self, data):
        """
        Check that the two password entries match.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        # Remove the confirmation password, it's not part of the User model
        validated_data.pop('password2')
        
        # --- FIX: Use direct key access instead of .get() ---
        # Since the fields are now required, they are guaranteed to be in validated_data.
        # Using direct access (e.g., validated_data['id_card_front']) is cleaner.
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            id_card_front=validated_data['id_card_front'],
            id_card_back=validated_data['id_card_back'],
            face_verification_image=validated_data['face_verification_image'],
            is_active=False # User remains inactive until OTP verification
        )
        return user
    
    
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data