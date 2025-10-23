from rest_framework import serializers
from .models import Plan, Subscription, Coupon

class PlanSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    class Meta:
        model = Plan
        fields = [
            'id','plan_type','name','features',
            'monthly_price_usd','yearly_price_usd',
            'max_live_events','admin_seats','boost_credits_per_month',
            'leads_enabled','heatmap_level','analytics_level',
        ]

    def get_features(self, obj):
        """
        Return features as a list instead of a single text block.
        Example: "Feature 1\nFeature 2\nFeature 3" → ["Feature 1", "Feature 2", "Feature 3"]
        """
        if not obj.features:
            return []

        return [f.strip() for f in obj.features.split('\n') if f.strip()]

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
    email = serializers.EmailField(required=True)
    plan_type = serializers.CharField()
    billing_cycle = serializers.ChoiceField(choices=['monthly','yearly'], default='monthly')
    coupon = serializers.CharField(required=False, allow_blank=True)
