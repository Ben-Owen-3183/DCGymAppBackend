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
    email = models.CharField(max_length=150)
    active = models.BooleanField(null=False, blank=True)

    class Meta:
        verbose_name_plural = "Membership Status"

    def __str__(self):
        return self.email

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

class AwaitingActivation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.CharField(max_length=150)
    name = models.CharField(max_length=300)


