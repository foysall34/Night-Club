
from django.urls import path
from .views import PlanListView, CreateCheckoutSessionView, MySubscriptionView, StripeWebhookView  
from .views import PaymentCancelView , PaymentSuccessView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plans-list'),
    path('subscribe/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('subscription/', MySubscriptionView.as_view(), name='my-subscription'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
]
