from django.db import models
from login.models import CustomUser

def upload_path(instances,filename):
    return 'avatars/'


class UserAvatar(models.Model):
    user = models.OneToOneField(CustomUser, unique=True, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=150)

class PasswordResets(models.Model):
    user = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    v_token = models.CharField(max_length=150)
    timestamp = models.DateField()
    locked = models.BooleanField()

class MembershipStatus(models.Model):
    customer_id = models.CharField(max_length=150, unique=True)
    email = models.CharField(max_length=150)
    mandate_id = models.CharField(max_length=150)
    subscription_id = models.CharField(max_length=150)
    active = models.BooleanField()

    class API_type(models.TextChoices):
        STRIPE = 'stripe'
        GO_CARDLESS = 'go_cardless'

    api_type = models.CharField(
        max_length=20,
        choices=API_type.choices,
        default=API_type.STRIPE,
    )

    def __str__(self):
        return self.email


class MainJointAccount(models.Model):
    main_joint_account = models.ForeignKey(
        MembershipStatus,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.main_joint_account.email

class LinkedAccount(models.Model):
    parent_account = models.ForeignKey(
        MainJointAccount,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    child_account = models.ForeignKey(
        MembershipStatus,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    def __str__(self):
        return self.child_account.email










#
