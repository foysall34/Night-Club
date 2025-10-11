from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# ==============================================================================
# PART 1: CLUB OWNER MODELS
# (This section remains the same as your original code)
# ==============================================================================

class ClubOwnerManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

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
    venue_city = models.CharField(max_length=100 , default='write city')
    link = models.CharField(max_length=300, default='link', blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

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

    # --- Important Django Fields ---
    is_staff = models.BooleanField(default=False)
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
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Club Owner'
        verbose_name_plural = 'Club Owners'

# ==============================================================================
# PART 2: NEW - REGULAR USER MODELS
# (This section is newly added for the 'User' role)
# ==============================================================================

class UserManager(BaseUserManager):
 
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Note: This will create a superuser of type User
        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Represents a regular User account.
    """
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    otp = models.CharField(max_length=4, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    is_staff = models.BooleanField(default=False) #false
    is_active = models.BooleanField(default=False) #false by default
    date_joined = models.DateTimeField(default=timezone.now)


    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="custom_user_set",  
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="custom_user_permissions_set", 
        related_query_name="user",
    )

  
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'



from django.db.models.signals import post_save
from django.dispatch import receiver
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
 
    music_preferences = models.JSONField(default=list, blank=True)
    ideal_vibes = models.JSONField(default=list, blank=True)
    crowd_atmosphere = models.JSONField(default=list, blank=True)
    nights_out = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(7)] 
    )

    def __str__(self):
        return f"{self.user.email}'s Profile"



# ==============================================================================
# PART 3: CLUB AND EVENT MODELS
# (This section remains the same)
# ==============================================================================

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
    owner = models.ForeignKey(ClubOwner, on_delete=models.CASCADE, related_name='club_profile', null=True)
    clubName = models.CharField(max_length=255, blank=True, null=True)
    club_type = models.ManyToManyField(ClubType, blank=True)
    vibes_type = models.ManyToManyField(Vibes_Choice, blank=True)
    dressCode = models.CharField(max_length=255, blank=True)
    ageRequirement = models.CharField(max_length=100, blank=True)
    coverCharge = models.CharField(max_length=255, blank=True)
    clubImageUrl = models.ImageField(upload_to='clubs/images/', max_length=500, blank=True, null=True)
    
    features = models.JSONField(default=dict)
    events = models.JSONField(default=dict)
    practicalInfo = models.JSONField(default=dict)
    contact = models.JSONField(default=dict)
    weekly_hours = models.JSONField(default=get_default_weekly_hours)
    reviews = models.JSONField(default=list) 

    def __str__(self):
        return self.clubName or f"Unnamed Club (ID: {self.id})"
    



#  write Your review code here 






class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('live', 'Live'),
    )

    club = models.ForeignKey(ClubProfile, on_delete=models.CASCADE, related_name='club_events')
    name = models.CharField(max_length=255, verbose_name="Event Name")
    date = models.DateField()
    time = models.TimeField()
    entry_fee = models.CharField(max_length=100, blank=True, help_text="e.g., $20 or Free")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} at {self.club.clubName}"

    class Meta:
        ordering = ['-date', '-time']

# ==============================================================================
# PART 4: LEGAL CONTENT MODELS
# (This section remains the same)
# ==============================================================================

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