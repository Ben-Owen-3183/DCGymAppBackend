import django.db.models
from django.core.management import BaseCommand
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from rest_framework.permissions import IsAuthenticated, AllowAny
from login.membership_status import member_status_checker
from DCGymAppBackend import settings
from membership.models import StripeCustomer, StripeSubscription, UserSubscriptionCancelled
import uuid
import json
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render
import logging
import stripe
from login.models import CustomUser




stripe.api_key = settings.STRIPE['private']


class Command(BaseCommand):
    def handle(self, *args, **options):
        """user = CustomUser.objects.get(email='admin@admin.com')

        stripe_customer: StripeCustomer = StripeCustomer.objects.get(user=user)

        pm = stripe.PaymentMethod.list(
            customer=stripe_customer.customer_id,
            type='card'
        )

        """

        products_data = stripe.Product.list()

        for product_data in products_data:
            print()
            print(product_data)
            print()
            print()