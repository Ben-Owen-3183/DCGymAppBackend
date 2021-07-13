from django.db import models

# Create your models here.
class TimeTable(models.Model):
    live = models.BooleanField(default=False);
    time_from = models.TimeField(max_length=150)
    time_to = models.TimeField(max_length=150)
    excercise = models.CharField(max_length=150)
    instructor = models.CharField(max_length=150)

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
