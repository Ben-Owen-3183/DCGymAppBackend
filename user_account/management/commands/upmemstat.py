from django.core.management.base import BaseCommand, CommandError
import logging
from datetime import datetime
import gocardless_pro
import stripe
from django.conf import settings
from django.db import transaction
from user_account.models import MembershipStatus

# cronjob command
# python3 manage.py upmemstat >> user_account/management/commands/logs.txt

# AN 55779911
# SORT 200000
client = gocardless_pro.Client(
    access_token=settings.GC_ACCESS_TOKEN,
    environment=settings.GC_ENVIRONMENT
)
stripe.api_key = settings.STRIPE_ACCESS_TOKEN
prompt = '[' + str(datetime.now()) + '] '

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS(prompt + 'starting task'))

            go_cardless_success = self.go_cardless_update()
            stripe_success = self.stripe_update()

            if stripe_success and go_cardless_success:
                self.stdout.write(self.style.SUCCESS(prompt + 'task finished correctly'))
            elif stripe_success or go_cardless_success:
                self.stderr.write(prompt + 'task partially failed')
            else:
                self.stderr.write(prompt + 'stripe and go_cardless update tasks failed')
        except Exception as e:
            self.stdout.write(prompt + 'Error: ' + str(e))


    def go_cardless_update(self):
        try:
            subs = client.subscriptions.list().records
            mandates = client.mandates.list().records
            customers = client.customers.list().records

            data = []
            for customer in customers:
                customer_data = []
                for mandate in mandates:
                    if customer.id == mandate.links.customer:
                        for sub in subs:
                            if sub.links.mandate == mandate.id:
                                customer_data.append({
                                    'email': customer.email,
                                    'customer': customer.id,
                                    'mandate': mandate.id,
                                    'subscription': sub.id,
                                    'status': sub.status,
                                })
                # check for duplicates
                length = len(customer_data)
                if length > 1:
                    data.append(self.go_cardless_pick_active_sub(customer_data))
                elif length == 1:
                    data.append(customer_data[0])

            self.gc_store_or_update_membership(data)
            return True
        except Exception as e:
            self.stdout.write(prompt + 'Go Cardless Error: ' + str(e))
            return False


    # if go cardless returns duplicate subscription
    def go_cardless_pick_active_sub(self, customer_data):
        for data in customer_data:
            if data['status'] == 'active':
                return data
        return customer_data[0]


    def find_existing_go_cardless_member(self, members, customer):
        for member in members:
            if member.customer == customer:
                return member
        return None


    def gc_store_or_update_membership(self, data):
        try:
            members = MembershipStatus.objects.filter(api_type='go_cardless')

            members_to_create = []
            with transaction.atomic():
                for api_member in data:
                    member = self.find_existing_go_cardless_member(
                        members, api_member['customer']
                    )
                    active = True if api_member['status'] == 'active' else False
                    # if member exists in system update row
                    if member != None:
                        member.email = api_member['email']
                        member.customer = api_member['customer']
                        member.mandate = api_member['mandate']
                        member.subscription = api_member['subscription']
                        member.active = active
                        member.save()
                    # if member is not in system add them
                    else:
                        members_to_create.append(
                            MembershipStatus(
                                api_type='go_cardless',
                                email=api_member['email'],
                                customer=api_member['customer'],
                                mandate=api_member['mandate'],
                                subscription=api_member['subscription'],
                                active=active,
                            )
                        )

            members.update()
            MembershipStatus.objects.bulk_create(members_to_create)
        except Exception as e:
            raise Exception('storing and updating go cardless membship data failed:  ' + str(e))


    def stripe_update(self):
        try:
            subs = stripe.Subscription.list()
            customers = stripe.Customer.list()

            data = []
            for customer in customers:

                for sub in subs:
                    if customer.id == sub.customer:
                        data.append({
                            'email': customer.email,
                            'customer': customer.id,
                            'subscription': sub.id,
                            'status': sub.status,
                        })
            self.stripe_store_or_update_membership(data)

            return True
        except Exception as e:
            self.stdout.write(prompt + 'Stripe Error: ' + str(e))
            return False


    def find_existing_stripe_member(self, members, customer):
        for member in members:
            if member.customer == customer:
                return member
        return None


    def stripe_store_or_update_membership(self, data):
        try:
            members = MembershipStatus.objects.filter(api_type='stripe')
            members_to_create = []
            with transaction.atomic():
                for api_member in data:
                    member = self.find_existing_stripe_member(
                        members, api_member['customer']
                    )
                    active = True if api_member['status'] == 'active' else False
                    # if member exists in system update row
                    if member != None:
                        member.email = api_member['email']
                        member.customer = api_member['customer']
                        member.subscription = api_member['subscription']
                        member.active = active
                        member.save()
                    # if member is not in system add them
                    else:
                        members_to_create.append(
                            MembershipStatus(
                                api_type='stripe',
                                email=api_member['email'],
                                customer=api_member['customer'],
                                subscription=api_member['subscription'],
                                active=active,
                            )
                        )
            members.update()
            MembershipStatus.objects.bulk_create(members_to_create)
        except Exception as e:
            raise Exception('storing and updating go cardless membship data failed:  ' + str(e))









#
