from user_account.models import MembershipStatus
import logging
import gocardless_pro
import stripe
from django.conf import settings

class member_status_checker():
    """
    does api check from existing data is not 100% accurate.
    Does not garentee that an active user will be set to active.
    For that you need to pull all existing data from apis.
    """
    def check_membership_status_from_existing(self, email, member_status):
        try:
            if member_status.api_type == 'go_cardless':
                return self.go_cardless_check_status_from_membership_data(email, member_status)
            elif member_status.api_type == 'stripe':
                return self.stripe_check_status_from_membership_data(email, member_status)
            raise Exception('API type "' + member_status.api_type + '" not recognised')
        except Exception as e:
            return False


    def stripe_check_status_from_membership_data(self, email, member_status):
        try:
            stripe.api_key = settings.STRIPE_ACCESS_TOKEN
            subscription = stripe.Subscription.retrieve(member_status.subscription)
            active = True if subscription.status == 'active' else False
            if active:
                print('is active')
                member_status.active = True
                member_status.save()
                return True
        except Exception as e:
            return False


    def go_cardless_check_status_from_membership_data(self, email, member_status):
        try:
            go_cardless = gocardless_pro.Client(
                access_token=settings.GC_ACCESS_TOKEN,
                environment=settings.GC_ENVIRONMENT
            )
            subscription = go_cardless.subscriptions.get(member_status.subscription)
            active = False
            try:
                active = True if subscription.status == 'active' else False
            except Exception as e:
                logging.exception('a')
                pass

            if active:
                member_status.active = True
                member_status.save()
                return True

            # fall back if the subscription ID is invalid or inactive
            return self.go_cardless_lazy_attempt_to_find_subscription(email, member_status, go_cardless)
        except Exception as e:
            return False


    """
    called if the existing subscription id is invalid or inactive.
    Attempts to find alternative active subscription.
    """
    def go_cardless_lazy_attempt_to_find_subscription(self, email, member_status, go_cardless):

        print("go cardless: sub is not active or not found...")
        try:
            customer_subs = go_cardless.subscriptions.list(
                params={"customer": member_status.customer}
            ).records

            if len(customer_subs) == 0:
                return False
            subscription = customer_subs[0]
            active = True if subscription.status == 'active' else False
            if subscription.id != member_status.subscription:
                member_status.mandate = ''
                member_status.subscription = subscription.id
            if not active:
                return False
            member_status.active = True
            member_status.save()

            return True
        except Exception as e:
            return False


    def user_is_active_member(email):
        try:
            member_status = MembershipStatus.objects.get(email=email)
            if member_status.active:
                return True
            return self.check_membership_status_from_existing(email, member_status)
        except Exception as e:
            return False
