# subscriptions/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.conf import settings
import stripe
from .models import Plan, Subscription, Coupon
from .serializers import PlanSerializer, SubscriptionSerializer, CreateCheckoutSerializer
from .utils import create_or_get_stripe_customer, attach_subscription_locally
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from owner.models import ClubOwner

stripe.api_key = settings.STRIPE_API_KEY

class PlanListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        plans = Plan.objects.all().order_by('monthly_price_usd')
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)

class CreateCheckoutSessionView(APIView):
    """
    POST:
    Create Stripe Checkout Session by Owner Email.
    Body:
    {
        "email": "owner@example.com",
        "plan_key": "starter",
        "billing_cycle": "monthly",
        "success_url": "https://yourapp.com/success",
        "cancel_url": "https://yourapp.com/cancel",
        "coupon": "FOMO50"   (optional)
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Owner email required
        email = request.data.get("email")
        if not email:
            return Response({"error": "Owner email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check owner existence
        try:
            owner = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

        plan_key = data['plan_key']
        billing_cycle = data['billing_cycle']
        success_url = data['success_url']
        cancel_url = data['cancel_url']
        coupon_code = data.get('coupon', None)

        # Find Plan
        try:
            plan = Plan.objects.get(key=plan_key)
        except Plan.DoesNotExist:
            return Response({"error": "Invalid plan_key"}, status=status.HTTP_400_BAD_REQUEST)

        price_id = plan.stripe_monthly_price_id if billing_cycle == 'monthly' else plan.stripe_yearly_price_id
        if not price_id:
            return Response({"error": "Price not configured for this plan/cycle"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create Stripe customer
        customer_id = create_or_get_stripe_customer(owner)

        # Create checkout session arguments
        session_args = {
            "payment_method_types": ["card"],
            "mode": "subscription",
            "customer": customer_id,
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
        }

        # Optional coupon
        if coupon_code:
            try:
                c = Coupon.objects.get(code__iexact=coupon_code, active=True)
                if c.stripe_coupon_id:
                    session_args["discounts"] = [{"coupon": c.stripe_coupon_id}]
                else:
                    sc = settings.STRIPE_COUPONS.get(coupon_code)
                    if sc:
                        session_args["discounts"] = [{"coupon": sc}]
            except Coupon.DoesNotExist:
                sc = settings.STRIPE_COUPONS.get(coupon_code)
                if sc:
                    session_args["discounts"] = [{"coupon": sc}]

        # Create Stripe checkout session
        try:
            session = stripe.checkout.Session.create(**session_args)
        except Exception as e:
            return Response(
                {"error": "Stripe session creation failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "checkout_url": session.url,
            "session_id": session.id,
            "email": owner.email,
            "plan": plan.name
        })



class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        owner = request.user.owner_profile
        sub = Subscription.objects.filter(owner=owner, status='active').first()
        if not sub:
            return Response({"subscription": None})
        data = SubscriptionSerializer(sub).data
        return Response(data)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # webhook should not require auth

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except ValueError:
            return Response(status=400)
        except stripe.error.SignatureVerificationError:
            return Response(status=400)

        # handle important events
        event_type = event['type']
        data_obj = event['data']['object']

        try:
            if event_type == 'checkout.session.completed':
                # when checkout completes, create local subscription
                # session may contain subscription id
                if data_obj.get('mode') == 'subscription':
                    stripe_sub_id = data_obj.get('subscription')
                    if stripe_sub_id:
                        stripe_sub = stripe.Subscription.retrieve(stripe_sub_id, expand=['items.data.price'])
                        attach_subscription_locally(stripe_sub)

            elif event_type in ('customer.subscription.updated', 'customer.subscription.created'):
                stripe_sub = stripe.Subscription.retrieve(data_obj.get('id'), expand=['items.data.price'])
                attach_subscription_locally(stripe_sub)

            elif event_type == 'customer.subscription.deleted':
                # mark as canceled locally
                stripe_sub_id = data_obj.get('id')
                try:
                    sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
                    sub.status = 'canceled'
                    sub.current_period_end = None
                    sub.save()
                except Subscription.DoesNotExist:
                    pass

            elif event_type == 'invoice.payment_succeeded':
                # payment succeeded - record history
                invoice = data_obj
                stripe_sub_id = invoice.get('subscription')
                if stripe_sub_id:
                    try:
                        sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
                        # create PaymentHistory
                        from .models import PaymentHistory
                        amt = (invoice.get('amount_paid') or 0) / 100.0
                        PaymentHistory.objects.create(
                            subscription=sub,
                            invoice_id=invoice.get('id'),
                            amount_paid=amt,
                            status='succeeded'
                        )
                    except Subscription.DoesNotExist:
                        pass

            # add other event handlers if you need
        except Exception:
            # avoid throwing 500 to Stripe — log exception in real project
            pass

        return Response(status=200)
