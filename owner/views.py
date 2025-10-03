# accounts/views.py

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
            return Response({"error": "এই ইমেল দিয়ে একটি সক্রিয় অ্যাকাউন্ট আগে থেকেই আছে।"}, status=status.HTTP_400_BAD_REQUEST)



        fs = FileSystemStorage(location=settings.TEMP_MEDIA_ROOT)
        
   
        profile_image_name = fs.save(validated_data['profile_image'].name, validated_data['profile_image'])
        id_front_page_name = fs.save(validated_data['id_front_page'].name, validated_data['id_front_page'])
        id_back_page_name = fs.save(validated_data['id_back_page'].name, validated_data['id_back_page'])

        # টেক্সট ডেটাগুলোকে একটি ডিকশনারিতে রাখুন
        session_data = {
            'full_name': validated_data['full_name'],
            'email': email,
            'password': validated_data['password'],
            'phone_number': validated_data['phone_number'],
            'venue_name': validated_data['venue_name'],
            'venue_address': validated_data['venue_address'],
            'link': validated_data.get('link'),
        }

        # ৩. ফাইল অবজেক্টের পরিবর্তে ফাইলের নাম/পাথ (স্ট্রিং) সেশনে যোগ করুন
        session_data['profile_image_path'] = profile_image_name
        session_data['id_front_page_path'] = id_front_page_name
        session_data['id_back_page_path'] = id_back_page_name
        
        request.session['registration_data'] = session_data
        
        # OTP তৈরি করে সেশনে সেভ এবং ইমেল পাঠানো
        otp = generate_otp()
        request.session['otp_data'] = {'otp': otp, 'timestamp': timezone.now().isoformat()}
        send_otp_email(email, otp)

        return Response({"message": "আপনার ইমেলে একটি OTP পাঠানো হয়েছে। অনুগ্রহ করে ভেরিফাই করুন।"}, status=status.HTTP_200_OK)

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
            return Response({"error": "অবৈধ অনুরোধ বা সেশনের মেয়াদ শেষ। অনুগ্রহ করে আবার নিবন্ধন করুন।"}, status=status.HTTP_400_BAD_REQUEST)

        timestamp = timezone.datetime.fromisoformat(otp_data['timestamp'])
        if timezone.now() > timestamp + timedelta(minutes=5):
            return Response({"error": "OTP-এর মেয়াদ শেষ।"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_data['otp'] == otp:
            user = ClubOwner.objects.filter(email=email).first()
            if not user:
                user = ClubOwner(username=email, email=email)

            full_name_parts = reg_data['full_name'].strip().split(' ', 1)
            user.first_name = full_name_parts[0]
            user.last_name = full_name_parts[1] if len(full_name_parts) > 1 else ''
            user.set_password(reg_data['password'])
            user.phone_number = reg_data['phone_number']
            user.venue_name = reg_data['venue_name']
            user.venue_address = reg_data['venue_address']
            user.link = reg_data.get('link')
            user.is_active = True
            user.save()

            # --- সমাধান: গন্তব্য ডিরেক্টরি তৈরি করুন ---
            
            # স্থায়ী ফোল্ডারগুলোর পাথ নির্ধারণ করুন
            images_dest_dir = os.path.join(settings.MEDIA_ROOT, 'proofs', 'images')
            ids_dest_dir = os.path.join(settings.MEDIA_ROOT, 'proofs', 'ids')

            # ফোল্ডারগুলো তৈরি করুন (যদি আগে থেকে না থাকে)
            os.makedirs(images_dest_dir, exist_ok=True)
            os.makedirs(ids_dest_dir, exist_ok=True)
            
            # --- ফাইল সরানোর কোড ---

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

            return Response({"message": "অ্যাকাউন্ট সফলভাবে যাচাই এবং তৈরি করা হয়েছে।"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "অবৈধ OTP।"}, status=status.HTTP_400_BAD_REQUEST)

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
        
        return Response({"message": "একটি নতুন OTP আপনার ইমেলে পাঠানো হয়েছে।"}, status=status.HTTP_200_OK)

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
                return Response({'error': 'আপনার অ্যাকাউন্টটি সক্রিয় নয়।'}, status=status.HTTP_401_UNAUTHORIZED)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
            else:
                return Response({'error': 'অবৈধ শংসাপত্র।'}, status=status.HTTP_401_UNAUTHORIZED)
        except ClubOwner.DoesNotExist:
            return Response({'error': 'ব্যবহারকারীকে খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({'message': 'পাসওয়ার্ড রিসেট করার জন্য OTP আপনার ইমেলে পাঠানো হয়েছে।'}, status=status.HTTP_200_OK)
        except ClubOwner.DoesNotExist:
            return Response({'error': 'ব্যবহারকারীকে খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

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