# Generated by Django 3.1.7 on 2021-08-03 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_stream', '0005_auto_20210803_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vimeolivestreams',
            name='name',
            field=models.CharField(max_length=250),
        ),
    ]
