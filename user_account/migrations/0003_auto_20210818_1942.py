# Generated by Django 3.1.7 on 2021-08-18 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0002_auto_20210818_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipstatus',
            name='email',
            field=models.CharField(max_length=150),
        ),
    ]
