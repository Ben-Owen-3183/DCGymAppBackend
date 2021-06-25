from django.db import models
from login.models import CustomUser

# Create your models here.
class Chat(models.Model):
    timestamp = models.DateTimeField(auto_now=True)


class ChatUser(models.Model):
    subscribed_chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)


class Messages(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now=True)
