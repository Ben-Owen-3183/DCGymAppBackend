# Generated by Django 3.1.7 on 2021-05-08 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0007_auto_20210508_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useravatar',
            name='image',
            field=models.ImageField(upload_to='avatars'),
        ),
    ]
