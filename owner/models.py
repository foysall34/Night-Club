# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class ClubOwner(AbstractUser):
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    venue_name = models.CharField(max_length=255)
    venue_address = models.CharField(max_length=255)
    
    profile_image = models.FileField(upload_to='proofs/images/')
    id_front_page = models.FileField(upload_to='proofs/ids/')
    id_back_page = models.FileField(upload_to='proofs/ids/')
    link = models.CharField(max_length=300, default='link', blank=True, null=True)

    verification_status = models.CharField(
        max_length=10,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    
    # OTP-এর জন্য নতুন ফিল্ড
    otp = models.CharField(max_length=4, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.email