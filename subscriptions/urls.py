
from django.urls import path
from .views import PlanListView, CreateCheckoutSessionView, MySubscriptionView, StripeWebhookView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plans-list'),
    path('subscribe/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('subscription/', MySubscriptionView.as_view(), name='my-subscription'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
