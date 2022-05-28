from django.urls import path, re_path
from . import views

urlpatterns = [
    path('status/', views.Status.as_view()),
    path('checkout_details/', views.PaymentIntent.as_view()),
    path('setup_intent/', views.SetupIntent.as_view()),
]