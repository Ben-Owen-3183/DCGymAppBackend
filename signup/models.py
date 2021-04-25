from django.db import models

# Create your models here.
class PotentialUser(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    clubmanager_id = models.CharField(max_length=150)
