# subscriptions/models.py
from django.db import models

class Plan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
    ]

    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    features = models.TextField(blank=True)


    stripe_monthly_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_yearly_price_id = models.CharField(max_length=255, blank=True, null=True)

  
    monthly_price_usd = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    yearly_price_usd = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)


    max_live_events = models.IntegerField(null=True, blank=True)  
    admin_seats = models.IntegerField(default=1)
    boost_credits_per_month = models.IntegerField(default=0)
    leads_enabled = models.BooleanField(default=False)
    heatmap_level = models.CharField(
        max_length=20, 
        choices=[("none", "None"), ("lite", "Lite"), ("pro", "Pro")],
        default="none"
    )
    analytics_level = models.CharField(
        max_length=20, 
        choices=[("basic", "Basic"), ("standard", "Standard"), ("advanced", "Advanced")],
        default="basic"
    )

    def __str__(self):
        return f"{self.name} (${self.monthly_price_usd}/month)"

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"



# subscriptions/models.py
from django.db import models
from django.utils import timezone
from owner.models import ClubOwner
from .models import Plan  
import uuid

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('canceled', 'Canceled'),
        ('trialing', 'Trialing'),
        ('past_due', 'Past Due'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(ClubOwner, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)

    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='inactive')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    boost_credits_left = models.IntegerField(default=0)
    admin_seats_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        return self.status == "active"

    def remaining_boosts(self):
        return self.boost_credits_left

    def __str__(self):
        return f"{self.owner.full_name} - {self.plan.name if self.plan else 'No Plan'}"

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"





class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)  # e.g., FOMO50
    stripe_coupon_id = models.CharField(max_length=255, blank=True, null=True)
    percent_off = models.PositiveIntegerField(default=0)
    duration_in_months = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.percent_off}% off for {self.duration_in_months} months)"




