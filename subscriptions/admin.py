from django.contrib import admin

from .models import Plan,Subscription, Coupon

# Register your models here.
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_price_usd', 'yearly_price_usd', 'max_live_events', 'boost_credits_per_month')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'plan', 'status', 'current_period_end', 'boost_credits_left')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percent_off', 'duration_in_months', 'active')