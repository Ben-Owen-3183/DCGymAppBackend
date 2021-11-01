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

    class Meta:
        verbose_name_plural = "Password Resets"


class MembershipStatus(models.Model):
    customer_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.CharField(max_length=150)
    mandate_id = models.CharField(max_length=150, null=True, blank=True)
    subscription_id = models.CharField(max_length=150, null=True, blank=True)
    active = models.BooleanField(null=True, blank=True)
    force_active = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Membership Status"

    class API_type(models.TextChoices):
        GO_CARDLESS = 'go_cardless'
        MANUAL = 'manual'

    api_type = models.CharField(
        max_length=20,
        choices=API_type.choices,
        default=API_type.MANUAL,
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



class UserDeviceID(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=250, null=False, blank=False)

    class Device_Type(models.TextChoices):
        IOS = 'ios'
        ANDROID = 'android'

    device_type = models.CharField(
        max_length=20,
        choices=Device_Type.choices,
        default=Device_Type.ANDROID,
    )




#
