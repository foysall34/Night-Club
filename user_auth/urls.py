from django.urls import path
# Import standard JWT refresh view (highly recommended to go with your LoginAPIView)
from rest_framework_simplejwt.views import TokenRefreshView 
from .views import (
    UserRegistrationAPIView,
    VerifyOTPAPIView,
    ResendOTPAPIView,
    LoginAPIView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
)



urlpatterns = [
    # Registration & Verification
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPAPIView.as_view(), name='resend-otp'),

    # Authentication
    path('login/', LoginAPIView.as_view(), name='login'),
    # Standard Simple JWT refresh endpoint (allows getting new access token using refresh token)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password Management (Authenticated)
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),

    # Password Recovery (Unauthenticated)
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    # This path captures the uidb64 and token needed by your ResetPasswordAPIView.post method
    path('reset-password/<uidb64>/<token>/', ResetPasswordAPIView.as_view(), name='reset-password'),
]