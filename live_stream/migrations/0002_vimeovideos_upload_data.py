# Generated by Django 3.1.7 on 2021-07-26 15:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('live_stream', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vimeovideos',
            name='upload_data',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 26, 15, 0, 14, 397450, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
