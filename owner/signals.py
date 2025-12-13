from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ClubOwner
from .utils import generate_otp, send_approval_email, send_rejection_email

@receiver(post_save, sender=ClubOwner)
def send_otp_on_approval(sender, instance, created, **kwargs):
    # New user create হলে return করো
    if created:
        return

    # Approve হলে OTP পাঠাও
    if instance.verification_status == "approved" and instance.otp is None:
        otp = generate_otp()
        instance.otp = otp
        instance.otp_created_at = timezone.now()
        instance.is_active = True
        instance.save()

        send_approval_email(instance.email, otp)

    # Reject হলে rejection mail
    if instance.verification_status == "rejected":
        send_rejection_email(instance.email)
