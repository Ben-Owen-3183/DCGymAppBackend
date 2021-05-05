from django.db import models
from login.models import CustomUser


class UserAvatar(models.Model):
    user = models.OneToOneField(CustomUser, unique=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=150)
    image = models.FileField(upload_to='Avatar')
