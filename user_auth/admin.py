# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# It's good practice to unregister the default Group model if you're not using it
# from django.contrib.auth.models import Group
# admin.site.unregister(Group)

@admin.register(User)
class UserAdminCustom(UserAdmin):
    """
    Custom admin configuration for the User model.
    """

    # --- List View Configuration ---
    # Defines the columns shown in the user list page.
    list_display = (
        'email',
        'username',
        'is_email_verified',
        'is_identity_verified',
        'is_staff',
        'is_active',
        'date_joined',
    )
    
    # Adds filter options to the right sidebar.
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'is_email_verified',
        'is_identity_verified',
        'groups',
    )

    # --- Edit/Detail View Configuration ---
    # Organizes the fields on the user's detail/edit page into logical sections.
    fieldsets = (
        # Section 1: Core User Info
        (None, {'fields': ('email', 'username', 'password')}),
        
        # Section 2: Verification Status and OTP
        ('Verification Status', {
            'fields': ('is_email_verified', 'is_identity_verified', 'otp', 'otp_expiry')
        }),

        # Section 3: Verification Documents (ID and Face Images)
        ('Verification Documents', {
            'classes': ('collapse',), # Makes this section collapsible
            'fields': ('id_card_front', 'id_card_back', 'face_verification_image'),
        }),

        # Section 4: Permissions
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),

        # Section 5: Important Dates
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # --- Add User Form Configuration ---
    # Customizes the form for creating a new user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password', 'password2'),
        }),
    )
    
    # --- Other Configurations ---
    # Defines fields that can be searched.
    search_fields = ('email', 'username')
    
    # Defines which fields are not editable.
    readonly_fields = ('last_login', 'date_joined')
    
    # Sets the default ordering in the list view.
    ordering = ('-date_joined',)

    # Note: Because we are inheriting from UserAdmin, we don't need to re-implement
    # the password hashing logic or the form for creating users. It's all handled for us.