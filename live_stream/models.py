from django.db import models


# Create your models here.
class VimeoVideos(models.Model):
    vimeo_id = models.CharField(max_length=100)
    name = models.TextField(max_length=250)
    video_url = models.TextField(max_length=250)
    thumbnail_link = models.TextField(max_length=250)
    last_updated = models.DateTimeField()
    upload_date = models.DateTimeField()

    class Type(models.TextChoices):
        OLD_STREAM = 'OldStream'
        FEED_VIDEO = 'Feed'

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )

class VimeoLiveStreams(models.Model):
    name = models.CharField(max_length=250)
    stream_url = models.TextField(max_length=250)
    chat_url = models.TextField(max_length=250)
    time_from = models.TimeField(max_length=50)
    time_to = models.TimeField(max_length=50)

    class Day(models.TextChoices):
        MONDAY = 'Monday'
        TUESDAY = 'Tuesday'
        WEDNESDAY = 'Wednesday'
        THURSDAY = 'Thursday'
        FRIDAY = 'Friday'
        SATURDAY = 'Saturday'
        SUNDAY = 'Sunday'

    day = models.CharField(
        max_length=20,
        choices=Day.choices,
        default=Day.MONDAY,
    )
