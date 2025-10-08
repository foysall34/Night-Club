
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
from .utils import generate_otp, send_otp_email

# api/register
class RegisterView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = ClubOwnerRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        email = validated_data['email']

        if ClubOwner.objects.filter(email=email, is_active=True).exists():
            return Response({"error": "email already exists"}, status=status.HTTP_400_BAD_REQUEST)



        fs = FileSystemStorage(location=settings.TEMP_MEDIA_ROOT)
        
   
        profile_image_name = fs.save(validated_data['profile_image'].name, validated_data['profile_image'])
        id_front_page_name = fs.save(validated_data['id_front_page'].name, validated_data['id_front_page'])
        id_back_page_name = fs.save(validated_data['id_back_page'].name, validated_data['id_back_page'])

        session_data = {
            'full_name': validated_data['full_name'],
            'email': email,
            'password': validated_data['password'],
            'phone_number': validated_data['phone_number'],
            'venue_name': validated_data['venue_name'],
            'venue_address': validated_data['venue_address'],
            'link': validated_data.get('link'),
        }

        session_data['profile_image_path'] = profile_image_name
        session_data['id_front_page_path'] = id_front_page_name
        session_data['id_back_page_path'] = id_back_page_name
        
        request.session['registration_data'] = session_data
        
     
        otp = generate_otp()
        request.session['otp_data'] = {'otp': otp, 'timestamp': timezone.now().isoformat()}
        send_otp_email(email, otp)

        return Response({"message": "OTP has been sent to your email. Please verify."}, status=status.HTTP_200_OK)

# api/verify-otp
class VerifyOTPView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        reg_data = request.session.get('registration_data')
        otp_data = request.session.get('otp_data')

        if not reg_data or not otp_data or reg_data['email'] != email:
            return Response({"error": "Invalid request or session expired. Please register again."}, status=status.HTTP_400_BAD_REQUEST)

        timestamp = timezone.datetime.fromisoformat(otp_data['timestamp'])
        if timezone.now() > timestamp + timedelta(minutes=5):
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_data['otp'] == otp:
            user = ClubOwner.objects.filter(email=email).first()
            if not user:
                user = ClubOwner(full_name=reg_data['full_name'], email=email)

            user.full_name = reg_data['full_name'] 
            user.set_password(reg_data['password'])
            user.phone_number = reg_data['phone_number']
            user.venue_name = reg_data['venue_name']
            user.venue_address = reg_data['venue_address']
            user.link = reg_data.get('link')
            user.is_active = True
            user.save()

    
            
       
            images_dest_dir = os.path.join(settings.MEDIA_ROOT, 'proofs', 'images')
            ids_dest_dir = os.path.join(settings.MEDIA_ROOT, 'proofs', 'ids')


            os.makedirs(images_dest_dir, exist_ok=True)
            os.makedirs(ids_dest_dir, exist_ok=True)
            


            # Profile Image
            src_path = os.path.join(settings.TEMP_MEDIA_ROOT, reg_data['profile_image_path'])
            dst_path = os.path.join(images_dest_dir, reg_data['profile_image_path'])
            shutil.move(src_path, dst_path)
            user.profile_image.name = os.path.join('proofs', 'images', reg_data['profile_image_path'])
            
            # ID Front
            src_path = os.path.join(settings.TEMP_MEDIA_ROOT, reg_data['id_front_page_path'])
            dst_path = os.path.join(ids_dest_dir, reg_data['id_front_page_path'])
            shutil.move(src_path, dst_path)
            user.id_front_page.name = os.path.join('proofs', 'ids', reg_data['id_front_page_path'])
            
            # ID Back
            src_path = os.path.join(settings.TEMP_MEDIA_ROOT, reg_data['id_back_page_path'])
            dst_path = os.path.join(ids_dest_dir, reg_data['id_back_page_path'])
            shutil.move(src_path, dst_path)
            user.id_back_page.name = os.path.join('proofs', 'ids', reg_data['id_back_page_path'])
            
            user.save()

            # সেশন পরিষ্কার করা
            del request.session['registration_data']
            del request.session['otp_data']

            return Response({"message": "Account has been successfully verified and created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

# api/resend-otp
class ResendOTPView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        reg_data = request.session.get('registration_data')

        
        
        otp = generate_otp()
        request.session['otp_data'] = {'otp': otp, 'timestamp': timezone.now().isoformat()}
        send_otp_email(email, otp)

        return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)

# api/log-in
class LoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = ClubOwner.objects.get(email=email)
            if not user.is_active:
                return Response({'error': 'Your account is not active.'}, status=status.HTTP_401_UNAUTHORIZED)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh), 'email': user.email, 'msg':'Login successful', 'access': str(refresh.access_token)})
            else:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        except ClubOwner.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

# api/forgot-password
class ForgotPasswordView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        try:
            user = ClubOwner.objects.get(email=email, is_active=True)
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_otp_email(email, otp)
            return Response({'message': 'OTP has been sent to your email for password reset.'}, status=status.HTTP_200_OK)
        except ClubOwner.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

# api/change-password
class ChangePasswordView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = ClubOwner.objects.get(email=email)
            if timezone.now() > user.otp_created_at + timedelta(minutes=5):
                return Response({'error': 'OTP-is expired'} , status=status.HTTP_400_BAD_REQUEST)

            if user.otp == otp:
                user.set_password(new_password)
                user.otp = None
                user.otp_created_at = None
                user.save()
                return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'invalid OTP।'}, status=status.HTTP_400_BAD_REQUEST)
        except ClubOwner.DoesNotExist:
            return Response({'error': 'can not find user'}, status=status.HTTP_404_NOT_FOUND)
        





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

# --- View 2: নির্দিষ্ট প্রোফাইল দেখা, আপডেট ও ডিলিট করার জন্য ---
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
        """
        নির্দিষ্ট ধরনের legal document রিটার্ন করে।
        """
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