# Generated by Django 3.2.6 on 2021-11-01 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0010_post_upload_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='upload_date',
        ),
        migrations.AlterField(
            model_name='post',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]
