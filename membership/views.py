import django.db.models
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from rest_framework.permissions import IsAuthenticated, AllowAny
from login.membership_status import member_status_checker
from DCGymAppBackend import settings
from .models import StripeCustomer, StripeSubscription, UserSubscriptionCancelled
import uuid
import json
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render
import logging
import stripe
from login.models import CustomUser
from datetime import datetime, timedelta

# Create your views here.


"""
Request Format
{
    data: {...} // request data
    version: {...} // client version
    type: { ios/android/web }
}

response format
{
    data: { }
    success: { true/false }
    human_errors: []
    dev_errors: []  
}
"""

stripe.api_key = settings.STRIPE['private']


def get_customer(user):
    customer: StripeCustomer
    try:
        customer = StripeCustomer.objects.get(user=user.id)
    except django.db.models.ObjectDoesNotExist:
        stripe_customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}"
        )
        customer = StripeCustomer.objects.create(
            user=user,
            customer_id=stripe_customer.id
        )
    return customer


class Status(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = {
                'membership_type': 'unknown',
                'stripe_public_key': settings.STRIPE['public']
            }

            if not request.user.is_authenticated:
                data['membership_type'] = 'no_membership'
            elif request.user.is_staff or request.user.is_superuser:
                data['membership_type'] = 'staff_membership'
            elif StripeSubscription.objects.exists(user=request.user.id):
                data['membership_type'] = 'virtual_membership'

            elif member_status_checker.user_is_active_member(request.user.email):
                data['membership_type'] = 'physical_membership'

            return Response({
                'data': data,
                'success': True,
                'human_errors': [],
                'dev_errors': [],
            })
        except Exception as e:
            return Response({
                'data': {},
                'success': False,
                'human_errors': ['Something went wrong'],
                'dev_errors': [str(e) if settings.DEBUG else 'n/a'],
            })


class GetPaymentMethods(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            stripe_customer: StripeCustomer = StripeCustomer.objects.get(user=request.user)

            cards_data = stripe.PaymentMethod.list(
                customer=stripe_customer.customer_id,
                type='card'
            )
            cards = list()
            for card_data in cards_data:
                exp_month = int(card_data['card']['exp_month'])
                exp_year = int(card_data['card']['exp_year'])
                card_time = datetime(day=1, month=exp_month, year=exp_year)
                expired = card_time < datetime.now()
                card = {
                    'exp_month': exp_month,
                    'exp_year': exp_year,
                    'last4': card_data['card']['last4'],
                    'expired': expired,
                    'payment_method_id': card_data['id']
                }
                cards.append(card)
            data = dict()
            data['cards'] = cards
            return Response({
                'data': data,
                'success': True,
                'human_errors': [],
                'dev_errors': [],
            })
        except Exception as e:
            return Response({
                'data': {},
                'success': False,
                'human_errors': ['Something went wrong fetching payment methods'],
                'dev_errors': [str(e) if settings.DEBUG else 'n/a'],
            })


class SetupIntent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            customer = get_customer(request.user)

            payment_intent_secret = stripe.SetupIntent.create(
                customer=customer.customer_id,
            )

            data = {
                'setup_intent_secret': payment_intent_secret['client_secret'],
            }

            return Response({
                'data': data,
                'success': True,
                'human_errors': [],
                'dev_errors': [],
            })

        except Exception as e:
            logging.exception(e)
            return Response({
                'data': {},
                'success': False,
                'human_errors': ['Something went wrong'],
                'dev_errors': [str(e) if settings.DEBUG else 'n/a'],
            })


class GetSubscriptionProducts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = {}

            products_data = stripe.Product.list()

            products = []
            for product_data in products_data:
                products.append(product_data)
            data['products'] = products

            return Response({
                'data': data,
                'success': True,
                'human_errors': [],
                'dev_errors': [],
            })
        except Exception as e:
            logging.exception(e)
            return Response({
                'data': {},
                'success': False,
                'human_errors': ['Something went wrong'],
                'dev_errors': [str(e) if settings.DEBUG else 'n/a'],
            })


class StartSubscription(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        human_errors = [str]
        try:
            is_member: bool = member_status_checker.user_is_active_member(request.user.email)
            if is_member:
                human_errors.append('You are already a member.')
                raise Exception('cannot start a subscription if user is already a member or is staff')

            if 'item_id' not in request.data:
                human_errors.append('Missing item')
                raise Exception('Missing item id')

            if 'payment_method_id' not in request.data:
                human_errors.append('Missing payment method')
                raise Exception('Missing payment_method_id')

            stripe.Subscription.cr




        except Exception as e:
            return Response({
                'data': {'public_key': settings.STRIPE['public']},
                'success': True,
                'human_errors': human_errors,
                'dev_errors': [str(e) if settings.DEBUG else 'n/a'],
            })


class PaymentIntent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            customer = get_customer(request.user)

            ephemeral_key_secret = stripe.EphemeralKey.create(
                customer=customer.customer_id,
                stripe_version='2020-08-27',
            )
            payment_intent_secret = stripe.PaymentIntent.create(
                amount=999,
                currency='gbp',
                customer=customer.customer_id,
                payment_method_types=["card"],
            )

            data = {
                'payment_intent_secret': payment_intent_secret['client_secret'],
                'ephemeral_key_secret': ephemeral_key_secret['secret'],
                'customer_id': customer.customer_id,
            }

            return Response({
                'data': data,
                'success': True,
                'human_errors': [],
                'dev_errors': [],
            })

        except Exception as e:
            logging.exception(e)
            return Response({
                'data': {},
                'success': False,
                'human_errors': ['Something went wrong'],
                'dev_errors': [str(e) if settings.DEBUG else 'n/a'],
            })


class StripeDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'data': {'public_key': settings.STRIPE['public']},
            'success': True,
            'human_errors': [],
            'dev_errors': [],
        })

