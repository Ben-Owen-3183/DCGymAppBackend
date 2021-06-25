from django.db import models
from login.models import CustomUser

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=150)
    content = models.CharField(max_length=2000, null=True)
    like_count = models.IntegerField(default=0)
    pinned = models.BooleanField(default=False);
    pinned_timed = models.BooleanField(default=False);
    pinned_time_days = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

class PostComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    like_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

class CommentReplies(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    like_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

# Likes
class PostLikes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class PostCommentLikes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)

class ReplyReplyLikes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment_reply = models.ForeignKey(CommentReplies, on_delete=models.CASCADE)
