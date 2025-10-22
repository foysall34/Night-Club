# subscriptions/utils.py
import stripe
from django.conf import settings
from .models import Subscription, Plan, Coupon
from owner.models import ClubOwner
from django.utils import timezone
from datetime import datetime

stripe.api_key = settings.STRIPE_API_KEY

def create_or_get_stripe_customer(owner: ClubOwner):
    """
    Create Stripe Customer for ClubOwner if not exists. Save stripe_customer_id to owner.stripe_customer_id if field exists.
    """
    # Try to use saved stripe_customer_id if model has attribute
    sc_id = getattr(owner, 'stripe_customer_id', None)
    if sc_id:
        # verify existence (optional)
        try:
            stripe.Customer.retrieve(sc_id)
            return sc_id
        except Exception:
            pass

    # create new customer with metadata so we can find them later
    customer = stripe.Customer.create(email=owner.email, name=owner.full_name, metadata={"owner_id": str(owner.id)})
    # save to owner if field exists
    if hasattr(owner, 'stripe_customer_id'):
        owner.stripe_customer_id = customer.id
        owner.save(update_fields=['stripe_customer_id'])
    return customer.id

def map_priceid_to_plan_key(price_id):
    """
    find plan key from settings.STRIPE_PRICE_IDS
    returns tuple (plan_key, billing_cycle) or (None, None)
    """
    mapping = getattr(settings, "STRIPE_PRICE_IDS", {})
    for k, v in mapping.items():
        if v == price_id:
            # k is like "starter_monthly" -> split
            parts = k.rsplit("_", 1)
            if len(parts) == 2:
                return parts[0], parts[1]  # plan_key, billing_cycle
            return k, None
    return None, None

def attach_subscription_locally(stripe_sub):
    """
    Given stripe.Subscription object (dict), create or update our Subscription model.
    """
    # stripe_sub may be a Stripe object or dict
    sub = stripe_sub
    customer_id = sub.get('customer')
    stripe_sub_id = sub.get('id')
    status = sub.get('status')
    current_start = sub.get('current_period_start')
    current_end = sub.get('current_period_end')

    # Find owner by stripe_customer_id in ClubOwner
    from owners.models import ClubOwner
    try:
        owner = ClubOwner.objects.get(stripe_customer_id=customer_id)
    except ClubOwner.DoesNotExist:
        # try to find metadata on stripe customer
        try:
            cus = stripe.Customer.retrieve(customer_id)
            owner_id = cus.get('metadata', {}).get('owner_id')
            owner = ClubOwner.objects.get(pk=owner_id)
        except Exception:
            return None

    # Determine plan from subscription's first item price id
    try:
        price_obj = sub['items']['data'][0]['price']
        price_id = price_obj.get('id') if isinstance(price_obj, dict) else price_obj.id
    except Exception:
        price_id = None

    plan_key, cycle = map_priceid_to_plan_key(price_id)
    plan = None
    if plan_key:
        try:
            plan = Plan.objects.get(key=plan_key)
        except Plan.DoesNotExist:
            plan = None

    # convert timestamps
    from django.utils import timezone
    if current_start:
        try:
            current_period_start = datetime.fromtimestamp(int(current_start), tz=timezone.utc)
        except Exception:
            current_period_start = None
    else:
        current_period_start = None

    if current_end:
        try:
            current_period_end = datetime.fromtimestamp(int(current_end), tz=timezone.utc)
        except Exception:
            current_period_end = None
    else:
        current_period_end = None

    # create/update local subscription
    obj, created = Subscription.objects.update_or_create(
        stripe_subscription_id=stripe_sub_id,
        defaults={
            'owner': owner,
            'plan': plan,
            'stripe_customer_id': customer_id,
            'status': status,
            'current_period_start': current_period_start,
            'current_period_end': current_period_end,
            'cancel_at_period_end': sub.get('cancel_at_period_end', False),
        }
    )

    # provision credit counters on creation or plan change
    if plan:
        obj.boost_credits_left = plan.boost_credits_per_month
        # reset admin seats used if needed
        if obj.admin_seats_used > plan.admin_seats:
            obj.admin_seats_used = plan.admin_seats
    obj.save()
    return obj
