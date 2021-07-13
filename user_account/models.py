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
    email = models.CharField(max_length=150, unique=True)
    customer = models.CharField(max_length=150)
    mandate = models.CharField(max_length=150)
    subscription = models.CharField(max_length=150)
    active = models.BooleanField()

    class API_type(models.TextChoices):
        STRIPE = 'stripe'
        GO_CARDLESS = 'go_cardless'

    api_type = models.CharField(
        max_length=20,
        choices=API_type.choices,
        default=API_type.STRIPE,
    )







#
