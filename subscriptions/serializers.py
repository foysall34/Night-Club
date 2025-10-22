# subscriptions/serializers.py
from rest_framework import serializers
from .models import Plan, Subscription, Coupon

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id','key','name','description',
            'monthly_price_usd','yearly_price_usd',
            'max_live_events','admin_seats','boost_credits_per_month',
            'leads_enabled','heatmap_level','analytics_level',
        ]

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    class Meta:
        model = Subscription
        fields = [
            'id','owner','plan','status','current_period_start','current_period_end',
            'cancel_at_period_end','boost_credits_left','admin_seats_used','stripe_subscription_id'
        ]
        read_only_fields = fields

class CreateCheckoutSerializer(serializers.Serializer):
    plan_key = serializers.CharField()
    billing_cycle = serializers.ChoiceField(choices=['monthly','yearly'], default='monthly')
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    coupon = serializers.CharField(required=False, allow_blank=True)
