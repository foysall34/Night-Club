
import os
import shutil
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from datetime import timedelta
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ClubOwner
from .serializers import *
# views.py

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.utils import timezone
from datetime import datetime, timedelta

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ClubOwner
from .serializers import ClubOwnerRegistrationSerializer, OwnerVerifyOTPSerializer
from .utils import generate_otp, send_otp_email

# views.py

import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import ClubOwner
from .serializers import ClubOwnerRegistrationSerializer

class OwnerRegisterView(generics.CreateAPIView):
    """
    View for registering a new Club Owner.
    """
    serializer_class = ClubOwnerRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and send OTP
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send OTP to user's email
        send_mail(
            'Your OTP for registration',
            f'Your OTP is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "User registered successfully. Please check your email for OTP."},
            status=status.HTTP_201_CREATED
        )

class OwnerVerifyOTPView(APIView):
    """
    View for verifying OTP and activating the user's account.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp and timezone.now() - user.otp_created_at < timedelta(minutes=5):
            user.is_active = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response({"message": "OTP verified and user activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

class OwnerResendOTPView(APIView):
    """
    View for resending OTP to the user's email.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate and send a new OTP
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send new OTP to user's email
        send_mail(
            'Your new OTP for registration',
            f'Your new OTP is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "New OTP has been sent to your email."}, status=status.HTTP_200_OK)

class OwnerLoginView(APIView):
    """
    View for Club Owner login.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

      
        user = authenticate(username=email, password=password)

        if user is not None:
            if not user.is_active:
                return Response(
                    {"error": "This account is not active. Please verify your OTP."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

class OwnerForgotPasswordView(APIView):
    """
    View for handling forgot password requests.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate and send a password reset token (you would typically use a more secure method)
        # For simplicity, we'll reuse the OTP mechanism
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send password reset OTP to user's email
        send_mail(
            'Password Reset Request',
            f'Your OTP to reset your password is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset OTP has been sent to your email."}, status=status.HTTP_200_OK)
        





# For  owner profile club

# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import ClubProfile ,ClubOwner
from .serializers import ClubProfileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
# View for listing all clubs and creating a new one
from .authentications import ClubOwnerAuthentication
from .serializers import ClubProfileSerializer



class ClubProfileListCreateAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
      
        user_profiles = ClubProfile.objects.filter(owner=request.user)
        serializer = ClubProfileSerializer(user_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
    
        serializer = ClubProfileSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        success_data = {
            "message": "Club Profile created successfully!",
            "club_details": serializer.data
        }
        return Response(success_data, status=status.HTTP_201_CREATED)

class ClubProfileRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk, user):
     
        try:
            return ClubProfile.objects.get(pk=pk, owner=user)
        except ClubProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
  
        club_profile = self.get_object(pk, request.user)
        serializer = ClubProfileSerializer(club_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
      
        club_profile = self.get_object(pk, request.user)
        serializer = ClubProfileSerializer(club_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        success_data = {
            "message": "Club Profile updated successfully!",
            "club_details": serializer.data
        }
        return Response(success_data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
    
        club_profile = self.get_object(pk, request.user)
        club_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ClubProfile
from .serializers import ClubProfileSerializer

class ClubProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
      
        profiles = ClubProfile.objects.all()
        serializer = ClubProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
      
        serializer = ClubProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


""" Club Event & Legal Content Views """

class OwnerClubListAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
      
        clubs = ClubProfile.objects.filter(owner=request.user)
        serializer = OwnerClubSerializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventListCreateAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
   
        events = Event.objects.filter(club__owner=request.user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
    
        serializer = EventSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
     
        try:
 
            return Event.objects.get(pk=pk, club__owner=user)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        event = self.get_object(pk, request.user)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def patch(self, request, pk, *args, **kwargs):
        event = self.get_object(pk, request.user)
        serializer = EventSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        event = self.get_object(pk, request.user)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from .models import LegalContent
from .serializers import LegalContentSerializer

class LegalContentView(APIView):
    """
    Retrieve a legal document (Privacy Policy or Terms of Service).
    """
    def get_document_type(self, type_slug):

        if type_slug == 'privacy-policy':
            return 'privacy_policy'
        elif type_slug == 'terms-of-service':
            return 'terms_of_service'
        return None

    def get(self, request, type_slug, format=None):
       
        content_type = self.get_document_type(type_slug)
        
        if not content_type:
            raise Http404

        try:
            document = LegalContent.objects.get(content_type=content_type)
        except LegalContent.DoesNotExist:
        
            return Response(
                {"detail": "Content not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = LegalContentSerializer(document)
        return Response(serializer.data)
    





from .authentications import ClubOwnerAuthentication 
from .serializers import WeeklyHoursSerializer
from .models import ClubProfile

class WeeklyHoursAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
     
        profiles = ClubProfile.objects.filter(owner=user)

        if not profiles.exists():
            raise Http404("Club Profile not found for this owner.")
        

        return profiles.last()

    def get(self, request, *args, **kwargs):
        club_profile = self.get_object(request.user)
        serializer = WeeklyHoursSerializer(club_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        club_profile = self.get_object(request.user)
        serializer = WeeklyHoursSerializer(club_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        success_data = {
            "message": "Weekly hours updated successfully!",
            "weekly_hours": serializer.data['weekly_hours']
        }
        return Response(success_data, status=status.HTTP_200_OK)
    



# clubs/views.py
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import ClubProfile, Review
from .serializers import ReviewSerializer, CreateReviewSerializer

class ClubReviewListCreateView(generics.ListCreateAPIView):
    """
    GET: list reviews for a club
    POST: create review for a club (rating required, text/image optional)
    """
    permission_classes = [permissions.IsAuthenticated]  # Allow any user (authenticated or not) to view reviews
    serializer_class = ReviewSerializer

    def get_queryset(self):
        club_id = self.kwargs['club_id']
        club = get_object_or_404(ClubProfile, id=club_id)
        return club.reviews.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateReviewSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        club = get_object_or_404(ClubProfile, id=self.kwargs['club_id'])
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(club=club, user=user)



#=========================================================================
#=========================================================================
#=========================================================================
    """************ For Custom User Authentication ************"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import User
from .serializers import (
    UserRegistrationSerializer, VerifyOTPSerializer, ResendOTPSerializer, UserLoginSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .userutils  import send_otp_email
from rest_framework.permissions import IsAuthenticated




# For Password Reset
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.core.mail import send_mail
from django.conf import settings
from owner.models import User 

class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send OTP email
        send_otp_email(user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Registration successful. Please check your email for an OTP to verify your account."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserVerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            if user.otp != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            
            # OTP expiry check (e.g., 5 minutes)
            if timezone.now() > user.otp_created_at + timedelta(minutes=5):
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.otp = None
            user.otp_created_at = None
            user.save()

            return Response({"message": "Account verified successfully. You can now log in."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserResendOTPAPIView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            if user.is_active:
                return Response({"message": "This account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            # Send a new OTP
            send_otp_email(user)
            return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = None
            user_type = None

            try:
                user_candidate = User.objects.get(email=email)

                if user_candidate.check_password(password):
                    user = user_candidate
                    user_type = 'user'
            except User.DoesNotExist:
             
                pass

        
            if user is None:
                try:
                    owner_candidate = ClubOwner.objects.get(email=email)
       
                    if owner_candidate.check_password(password):
                        user = owner_candidate
                        user_type = 'owner'
                except ClubOwner.DoesNotExist:
          
                    pass
 
            if user is not None:
     
                if not user.is_active:

                    return Response({
                        "error": "Account not verified. Please verify your account with OTP."
                    }, status=status.HTTP_401_UNAUTHORIZED)

                refresh = RefreshToken.for_user(user)
                
                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user_type, 
                    'email': user.email,
                    'message': 'Login successful.'
                }
                return Response(response_data, status=status.HTTP_200_OK)

            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token_generator = PasswordResetTokenGenerator()
                uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
                token = token_generator.make_token(user)
                
                reset_link = f"http://your-frontend-domain/reset-password/{uidb64}/{token}/"
                
                # Send email
                subject = 'Password Reset Request'
                message = f'Hi {user.full_name},\n\nPlease click on the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

                return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # Still return a success message to not reveal which emails are registered
                return Response({'message': 'If an account with this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResetPasswordAPIView(APIView):
    def post(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data, context={'uidb64': uidb64, 'token': token})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



# for dummy response google api 


# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests


class NearbyBarsView(APIView):

    def get(self, request):
        try:

            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
            
            radius = request.query_params.get('radius', 5000)

            if not lat or not lng:
                return Response(
                    {"error": "Latitude (lat) and Longitude (lng) are required parameters."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_key = settings.GOOGLE_MAPS_API_KEY
            
            places_url = (
                f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                f"?location={lat},{lng}"
                f"&radius={radius}"
                f"&type=bar|night_club"
                f"&key={api_key}"
            )
            
            places_response = requests.get(places_url)
            places_data = places_response.json()

            if places_data['status'] != 'OK':
                return Response(
                    {"error": f"Google Places API error: {places_data.get('error_message', places_data['status'])}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            bars = places_data.get('results', [])
            if not bars:
                return Response({"message": "No nearby bars or night clubs found."}, status=status.HTTP_200_OK)

            destination_locations = '|'.join([
                f"{bar['geometry']['location']['lat']},{bar['geometry']['location']['lng']}"
                for bar in bars
            ])

            distance_url = (
                f"https://maps.googleapis.com/maps/api/distancematrix/json"
                f"?origins={lat},{lng}"
                f"&destinations={destination_locations}"
                f"&key={api_key}"
            )
            
            distance_response = requests.get(distance_url)
            distance_data = distance_response.json()

            if distance_data['status'] != 'OK':
                return Response(
                    {"error": f"Google Distance Matrix API error: {distance_data.get('error_message', distance_data['status'])}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            results = []
            for i, bar in enumerate(bars):
                distance_info = distance_data['rows'][0]['elements'][i]
                
                if distance_info['status'] == 'OK':
                    results.append({
                        "name": bar.get('name'),
                        "address": bar.get('vicinity'),
                        "distance": distance_info['distance']['text'],
                        "duration": distance_info['duration']['text'],
                        "rating": bar.get('rating', 'N/A'),
                    })
            
            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DummyNearbyBarsView(APIView):
   
    def get(self, request):

        dummy_data = [
            {
                "name": "Smuggler's Cove",
                "address": "650 Gough St, San Francisco",
                "distance": "1.5 km",
                "duration": "19 mins",
                "rating": 4.7
            },
            {
                "name": "Toronado",
                "address": "547 Haight St, San Francisco",
                "distance": "2.1 km",
                "duration": "26 mins",
                "rating": 4.6
            },
            {
                "name": "The Old Fashioned",
                "address": "23 N Pinckney St, Madison",
                "distance": "5.3 km",
                "duration": "12 mins",
                "rating": 4.8
            }
        ]
        

        return Response(dummy_data, status=status.HTTP_200_OK)