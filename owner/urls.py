# accounts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('log-in/', LoginView.as_view(), name='log-in'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('clubs/', ClubProfileListCreateAPIView.as_view(), name='club-list-create'),
    path('club-profiles/<int:pk>/', ClubProfileListCreateAPIView.as_view(), name='club-profile-detail'),
    path('legal/<slug:type_slug>/', LegalContentView.as_view(), name='legal-content'),
    path('club-profile/weekly-hours/', WeeklyHoursAPIView.as_view(), name='club-profile-weekly-hours'),

]