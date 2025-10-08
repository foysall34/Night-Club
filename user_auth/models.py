# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone



# Helper class to create dynamic upload paths for user files
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profiles/<user_id>/<filename>
    return f'profiles/{instance.id}/{filename}'

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model supporting email as the unique identifier.
    """
    # BUG 2 FIX: The model fields are now structured correctly.
    # All fields are defined first.

    # --- Standard Fields ---
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)

    # --- Verification Fields ---
    otp = models.CharField(max_length=4, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_identity_verified = models.BooleanField(default=False)

    # --- ID & Face Verification Images ---
    id_card_front = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    id_card_back = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    face_verification_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)

    # --- Django's Required Fields ---
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  #false by default
    date_joined = models.DateTimeField(default=timezone.now)

    # --- Permissions and Groups (with related_name to avoid clashes) ---
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="user_auth_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_auth_user_permissions_set",
        related_query_name="user",
    )

    # --- Manager and Required Settings ---
    # The duplicate 'objects = UserManager()' has been removed.
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email