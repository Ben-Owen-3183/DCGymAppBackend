# Generated by Django 3.1.7 on 2021-05-08 15:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0008_auto_20210508_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useravatar',
            name='image',
            field=models.ImageField(upload_to=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
        ),
    ]
