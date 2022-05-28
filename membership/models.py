from django.db import models
from login.models import CustomUser


class StripeCustomer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True)
    customer_id = models.CharField(max_length=255)


class StripePaymentMethods(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True)
    stripe_customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE, unique=True)
    cards = models.TextField(editable=True)


class StripeSubscription(models.Model):
    customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True)
    status = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    upcoming_payments = models.TextField(editable=True)
    timestamp = models.DateTimeField(auto_now=True)


class UserSubscriptionCancelled(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)




