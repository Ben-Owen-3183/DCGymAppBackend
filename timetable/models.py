from django.db import models

# Create your models here.
class CustomUserManager(BaseUserManager):
    live = models.BooleanField(default=False);
    time_from = models.CharField(max_length=150)
    time_from = models.CharField(max_length=150)
