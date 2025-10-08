from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone

# BUG FIX 1: Added the required UserManager
class ClubOwnerManager(BaseUserManager):
    """
    Custom manager for the ClubOwner model.
    """
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        # PermissionsMixin requires is_staff to be present for superuser creation
        # Since the field is missing, we must set these defaults for the command to work
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Added for completeness

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # We are creating a user that will have these flags, even if the fields are not in the database.
        # This is required for the createsuperuser command to succeed.
        return self.create_user(email, full_name, password, **extra_fields)


class ClubOwner(AbstractBaseUser, PermissionsMixin):
    """
    Represents a Club Owner user account.
    """
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    # --- Profile Information ---
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    venue_name = models.CharField(max_length=255)
    venue_address = models.CharField(max_length=255)
    link = models.CharField(max_length=300, default='link', blank=True, null=True)

    # --- Verification Documents ---
    profile_image = models.FileField(upload_to='proofs/images/')
    id_front_page = models.FileField(upload_to='proofs/ids/')
    id_back_page = models.FileField(upload_to='proofs/ids/')
    
    # --- Status and OTP ---
    verification_status = models.CharField(
        max_length=10,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    otp = models.CharField(max_length=4, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    # --- Important Django Fields (Added for compatibility) ---
    # NOTE: These are necessary for the admin and authentication to work properly.
    is_staff = models.BooleanField(default=False) #false by default
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # --- Permissions and Groups (with unique related_name) ---
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="club_owner_set",
        related_query_name="club_owner",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="club_owner_permissions_set",
        related_query_name="club_owner",
    )

    # --- Manager and Required Settings ---
    objects = ClubOwnerManager()

    USERNAME_FIELD = 'email'
    # BUG FIX 2: Changed 'username' to 'full_name' since 'username' does not exist.
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
    
    # BUG FIX 4: Replaced the incorrect method with the correct Meta class
    class Meta:
        verbose_name = 'Club Owner'
        verbose_name_plural = 'Club Owners'
    

# For owner club 


from django.db import models

class ClubType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Vibes_Choice(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name


def get_default_weekly_hours():
  
    default_time = {"start_time": "10:00", "end_time": "18:00"} 
    return {
        "monday": default_time,
        "tuesday": default_time,
        "wednesday": default_time,
        "thursday": default_time,
        "friday": default_time,
        "saturday": default_time,
        "sunday": default_time,
    }





class ClubProfile(models.Model):

    
    owner = models.ForeignKey(ClubOwner, on_delete=models.CASCADE, related_name='club_profile' , null=True)
    clubName = models.CharField(max_length=255 , blank=True , null=True) 
    club_type = models.ManyToManyField(ClubType, blank=True)
    vibes_type= models.ManyToManyField(Vibes_Choice, blank=True)
    dressCode = models.CharField(max_length=255, blank=True)
    ageRequirement = models.CharField(max_length=100, blank=True)
    coverCharge = models.CharField(max_length=255, blank=True)
    clubImageUrl = models.ImageField(upload_to='clubs/images/', max_length=500, blank=True, null=True)
    
    features = models.JSONField(default=dict)
    events = models.JSONField(default=dict)
    practicalInfo = models.JSONField(default=dict)
    contact = models.JSONField(default=dict)
    weekly_hours = models.JSONField(default=get_default_weekly_hours)

    def __str__(self):
          return self.clubName or f"Unnamed Club (ID: {self.id})"
    


# For club weekly Hours 




# Term & Conditions

# api/models.py

from django.db import models

class LegalContent(models.Model):

    CONTENT_TYPE_CHOICES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_of_service', 'Terms of Service'),
    ]

    content_type = models.CharField(
        max_length=20, 
        choices=CONTENT_TYPE_CHOICES, 
        unique=True, 
        help_text="The type of the legal document."
    )
    title = models.CharField(max_length=255)
    content = models.TextField(
        help_text="The main content of the document. You can use HTML for formatting."
    )
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_content_type_display()

    class Meta:
        verbose_name = "Legal Content"
        verbose_name_plural = "Legal Contents"
        ordering = ['content_type']