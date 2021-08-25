from django.core.management.base import BaseCommand, CommandError
import logging
from datetime import datetime, timedelta
import gocardless_pro
import stripe
from django.conf import settings
from django.db import transaction
from user_account.models import MembershipStatus
from user_account.models import LinkedAccount


# AN 55779911
# SORT 200000
client = gocardless_pro.Client(
    access_token=settings.GC_ACCESS_TOKEN,
    environment=settings.GC_ENVIRONMENT
)

prompt = '[' + str(datetime.now()) + '] '

linked_accounts = LinkedAccount.objects.all()
members = MembershipStatus.objects.filter(api_type='go_cardless')
manual_members = MembershipStatus.objects.filter(api_type='manual')

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS(prompt + 'starting task'))

            go_cardless_success = self.go_cardless_update()

            if go_cardless_success:
                self.stdout.write(self.style.SUCCESS(prompt + 'task finished correctly'))
            else:
                self.stderr.write(prompt + 'go_cardless / customer update tasks failed')
        except Exception as e:
            self.stdout.write(prompt + 'Error: ' + str(e))


    def go_cardless_update(self):
        customers_updated = self.go_cardless_update_customers()
        customer_status_updated = self.go_cardless_update_customer_status()
        return customers_updated and customer_status_updated


    def go_cardless_update_customer_status(self):
        try:
            datetime_now = datetime.now()
            td = timedelta(days=31) ########### GIVING 31 days of freedom
            datetime_from = datetime_now - td
            payments_by_mandate = {}
            for payment in client.payments.all(params={"charge_date[gte]": str(datetime_from.date()), "limit": 500}):
                payments_by_mandate[payment.links.mandate] = payment.status

            with transaction.atomic():
                for member in members :
                    try:
                        if member.mandate_id in payments_by_mandate:
                            payment_status = payments_by_mandate[member.mandate_id]
                            if self.payment_is_worthy_of_active_member(payment_status):
                                member.active = True
                                member.save()
                            elif self.has_active_linked_account(member):
                                member.active = True
                                member.save()
                            else:
                                member.active = False
                                member.save()
                        elif self.has_active_linked_account(member):
                            member.active = True
                            member.save()
                        else:
                            member.active = False
                            member.save()
                    except Exception as e:
                        pass

            members.update()

            return True
        except Exception as e:
            logging.exception('Go Cardless Error (updating customer status):')
            self.stdout.write(prompt + 'Go Cardless Error: ' + str(e))
            return False


    """
    Deactivates none existant go cardless customers,
    and adds new accounts with active set to False
    """
    def go_cardless_update_customers(self):
        try:
            members_to_create = []
            customers = []
            mandate_dict = {}

            for customer in client.customers.all(params={'limit':500}):
                customers.append(customer)

            for mandate in client.mandates.all(params={'limit':500, 'status': 'active'}):
                mandate_dict[mandate.links.customer] = mandate.id

            with transaction.atomic():
                for customer in customers:
                    member = self.find_existing_go_cardless_member(customer)
                    if member != None:
                        member.email = customer.email
                        member.mandate_id = mandate_dict[customer.id]
                        member.save()
                    # if member is not in system add them
                    else:
                        if not self.member_exists_as_manual(customer) and customer.id in mandate_dict:
                            members_to_create.append(
                                MembershipStatus(
                                    api_type='go_cardless',
                                    email=customer.email,
                                    customer_id=customer.id,
                                    mandate_id=mandate_dict[customer.id],
                                    active=False,
                                )
                            )
            members.update()
            MembershipStatus.objects.bulk_create(members_to_create)
            return True
        except Exception as e:
            self.stdout.write(prompt + 'Go Cardless Error (updating customers): ' + str(e))
            return False


    def find_existing_go_cardless_member(self, customer):
        for member in members:
            if member.customer_id == customer.id:
                return member
        return None

    def member_exists_as_manual(self, customer):
        for member in manual_members:
            if member.email == customer.email:
                return True
        return False

    """
    checks to see if none paying member is linked to a paying account
    i.e. joint/family account
    """
    def has_active_linked_account(self, member):
        for linked_account in linked_accounts:
            if linked_account.child_account.id == member.id and linked_account.parent_account.main_joint_account.active == True:
                return True
        return False


    def payment_is_worthy_of_active_member(self, status):
        if status == 'confirmed' or status == 'paid_out':
            return True
        return False





#
