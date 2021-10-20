from user_account.models import MembershipStatus
import logging
import gocardless_pro
import stripe
from django.conf import settings
from login.models import CustomUser

class member_status_checker():

    def user_is_active_member(email):
        try:
            try:
                user = CustomUser.objects.get(email=email);
                if user.is_staff or user.is_superuser:
                    return True
            except:
                pass

            member_status = MembershipStatus.objects.filter(email=email)
            length = len(member_status)
            
            if length == 0:
                return False
            elif length == 1:
                return member_status[0].active
            else:
                for member_instance in member_status:
                    if member_instance.active == True:
                        return True
            return False
        except Exception as e:
            return False
