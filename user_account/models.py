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
