# Generated by Django 3.1.7 on 2021-08-07 19:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0005_auto_20210807_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video_name',
            field=models.CharField(default=datetime.datetime(2021, 8, 7, 19, 41, 49, 701653, tzinfo=utc), max_length=250),
            preserve_default=False,
        ),
    ]